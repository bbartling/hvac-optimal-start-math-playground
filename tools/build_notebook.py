"""Generate the readable notebook; implementations live in hvac_optimal/."""
from pathlib import Path
import json
import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
cells = []


def md(text):
    cells.append(nbf.v4.new_markdown_cell(text.strip()))


def code(text, *, tags=None):
    cell = nbf.v4.new_code_cell(text.strip())
    if tags:
        cell.metadata['tags'] = tags
    cells.append(cell)


md("""
# Optimal start **and** stop: a BAS reference, several estimators, one honest experiment

Learn how a source-traceable BAS state machine schedules temperature recovery, how each AHU learns independently,
and how to compare PNNL-style estimators without changing the operating rules underneath them.

**What is optimal start?** A building may be unoccupied overnight but need comfortable rooms when people arrive.
Starting every air handler two hours early wastes conditioning time on mild mornings and can still be too late on
extreme days. Optimal start estimates how long heating or cooling will take, then starts before scheduled occupancy.
For example, a 30-minute recovery estimate for an 8:00 AM occupied schedule suggests a 7:30 AM start, subject to the
original BAS sequence. The controller learns from measured temperature response. Optimal stop estimates when
conditioning can stop before scheduled departure while temperatures remain within the occupied comfort limits.

**The research behind this project.** We implement and examine adaptations of four optimal-start models from
PNNL research: Kim, Yu, Lutes and Katipamula, *Implementation and validation of optimal start control strategy for
air conditioners and heat pumps*, Applied Thermal Engineering 257 (2024), 124256.
[Find the paper through its DOI](https://doi.org/10.1016/j.applthermaleng.2024.124256).
The repository copy is `PNNL_Paper/Optimal Start Control for ACs and HPs.pdf`. The supplied research code,
paper equations and our event-based adaptations are distinguished in `docs/model-provenance.md`; they are not
claimed to be identical implementations.

**Why use the Kaggle simulator?** The Smart Buildings competition's official simulator provides repeatable
building, weather, AHU and VAV-zone dynamics for testing these ideas beyond a single recorded recovery curve.
Our installed kit supplies **six simulated buildings, 34 AHU systems serving mapped VAV zones, and 30 building/weather
scenarios across five weather cities**. Each AHU has independent learners and its own representative zone sample.
These are simulated buildings, not 34 field installations.

We completed **60 full 30-day runs** comparing native and adaptive policies, with all research estimators evaluated
as shadow forecasts, plus **240 shorter runs** exercising each of the eight candidate start policies across all
30 scenarios. The shorter runs establish integration rather than full-month performance for every candidate.
This tests research-derived algorithms in the competition simulator; it does not reproduce PNNL's field study or
establish savings in real buildings. Later sections report measured results and differing arrival objectives.

**Three separate layers:** `reference.py` owns native start/stop behavior; `models.py` estimates durations;
`replay.py` records predictions before outcomes and training. The standard-library driver also accepts JSONL for IoT adapters.

This is an educational notebook, **not a submitted competition policy** and not field validation of the Python port.
The supplied Java is the owner's production behavior reference. Its long field history does not transfer automatically
to a translation: executable tests compare the visible Java branches under documented time/status stubs.
""")
md("""
## 1. Run offline

Locally: install `.[notebook]` from this repository. On Kaggle: attach the exported tutorial dataset containing
`hvac_optimal_driver.zip` and `data/`, then Run All with internet **off**. No moving GitHub download is used.
The code below finds that driver; the algorithms remain readable Python modules rather than hidden notebook cells.
""")
code("""
import sys
from pathlib import Path
import importlib.util

if importlib.util.find_spec('hvac_optimal') is None:
    archives = list(Path.cwd().glob('hvac_optimal_driver.zip'))
    archives += sorted(Path('/kaggle/input').rglob('hvac_optimal_driver.zip'))
    extracted = sorted(Path('/kaggle/input').rglob('hvac_optimal/__init__.py'))
    if archives:
        sys.path.insert(0, str(archives[0]))
    elif extracted:  # Dataset upload tools may unpack the driver ZIP.
        sys.path.insert(0, str(extracted[0].parents[1]))
    else:
        raise FileNotFoundError('Attach the exported offline tutorial dataset first.')

import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display
from hvac_optimal import Config, Inputs, OptimizedStartStop
from hvac_optimal.sampling import ZoneSampler
from hvac_optimal.replay import load_recovery_events, run_replay, ResearchSelector
from hvac_optimal.tutorial import (find_data, reference_learning_demo, plot_replay_summary,
                                   plot_error_history, plot_selection, simulation_table, plot_ahu_trace)

DATA = find_data()
plt.rcParams.update({'figure.dpi': 110, 'axes.spines.top': False, 'axes.spines.right': False,
                     'axes.grid': True, 'grid.alpha': .18, 'font.size': 10})
print('Verified offline data:', DATA)
""")
md("""
## 2. One AHU, its own representative temperature

Default: select **30%** of that AHU's mapped zones, split as evenly as possible between **exterior and interior** zones.
Keep the sample fixed throughout a run. The selected sensors have equal averaging weights unless BAS weights are supplied.
An odd sample or a small exterior/interior pool cannot always be perfectly balanced; the receipt explains the actual result.

Types come from explicit BAS configuration or simulator geometry, never zone-name guesses. Unknown types are reported.
This is an **input adapter**, not a new guard that stops the reference from learning. The units of the weighted mean
are the units of the supplied sensors.
""")
code("""
zones = [f'zone-{i}' for i in range(10)]
zone_types = {z: ('exterior' if i < 6 else 'interior') for i, z in enumerate(zones)}
temperatures = {z: 65.0 + i for i, z in enumerate(zones)}
sampler = ZoneSampler('AHU-example', zones, fraction=.30, zone_types=zone_types, seed=7)
representative_temp, receipt = sampler.read(temperatures, with_receipt=True)
display(pd.DataFrame({'zone': sampler.selected_zone_ids,
                      'type': [zone_types[z] for z in sampler.selected_zone_ids],
                      'temperature_F': [temperatures[z] for z in sampler.selected_zone_ids],
                      'weight': [receipt['weights'][z] for z in sampler.selected_zone_ids]}))
print(f'Representative AHU temperature: {representative_temp:.2f} °F')
print('Selected groups:', receipt['selected_group_counts'], '| fallback:', receipt['fallback_reason'])
""")
md("""
## 3. The BAS state machine: preserve its learning rules

```text
scan -> analyze the PREVIOUS operating mode -> calculate start/stop lead
     -> apply the original command-time rules -> emit value + null status -> remember mode

learn only when native dynamic adjustment is enabled, analysis is unfinished,
space-temperature status is valid, and temperature moved in the required direction:
    comfort crossed OR schedule changed -> observe elapsed minutes / temperature change
    parameter <- (2 * old_parameter + observation) / 3       # default multiplier = 2
```

There are **four independent minutes/degree parameters**: heating/cooling runtime for start and heating/cooling drift
for stop. This is not an EMA of degrees/minute. A small correct-direction response at the schedule transition can learn
even when full comfort recovery is unfinished. **No invented minimum-temperature-change, sample-count, rate-cap,
cooldown or outlier gate is added to this reference.**

Native optimized stop is an active **FALSE with non-null status**; FALSE with null status means no override.
Clock equality, earliest times, latches and numeric quirks are preserved and explained in `docs/reference-contract.md`.
""")
code("""
learning = pd.DataFrame(reference_learning_demo())
columns = ['case', 'temperature_change', 'elapsed_minutes', 'target_reached',
           'old_minutes_per_degree', 'observed_minutes_per_degree', 'new_minutes_per_degree']
display(learning[columns].round(4))
ax = learning.plot.bar(x='case', y=['old_minutes_per_degree', 'new_minutes_per_degree'],
                       color=['#a9b8c8', '#267c9c'], figsize=(10, 3.8), rot=15)
ax.set(ylabel='Minutes per °F', title='All four native learners update on eligible partial responses')
plt.tight_layout(); plt.show()
""")
md("""
### Controller without NumPy or pandas

**The existing controller and all eight estimators use Python's standard library only.** NumPy, pandas and Matplotlib
belong to this notebook's analysis and charts. A controller can run the same driver and equations without them;
there is no need to substitute a different learning algorithm.

For a small BAS controller, the native **minutes-per-degree** learner is the simplest starting point. Its learning
arithmetic uses only multiplication, division and addition, with four separate learned values:

```text
observed_minutes_per_degree = elapsed_minutes / measured_directional_temperature_change
updated = (old * old_parameter_multiplier + observed_minutes_per_degree) / (old_parameter_multiplier + 1)
```

Call that update only through the original state machine's eligibility checks. Keep the original float32 arithmetic,
time handling, start/stop latches and command value/null status when porting the native implementation. No extra
minimum-change or sample-count gate is required. The separate `LinearRateEMA` averages degrees/minute; averaging
reciprocals gives a different answer, so it is **not** an equivalent rewrite of the native learner.

| Algorithm | What vanilla Java needs |
| --- | --- |
| Native start/stop | Primitive scalar arithmetic; four learned minutes/degree values plus the original state machine |
| PNNL M1–M3 | Scalar coefficient formulas and short primitive arrays for coefficient history; no matrix solver |
| PNNL M4 | Scalar sums and `Math.log` / `Math.pow`; fixed-cadence fitting is simplest |
| Median ensemble | Four predictions, a small sort, and separate history banks |

M4's fixed-cadence fit accumulates `sum(previous_error * error)` and `sum(previous_error * previous_error)`.
Irregular sampling uses the existing scalar search and needs its sample pairs; do not treat irregular samples as
equally spaced to shorten the code. Java's built-in `Math` provides the logarithms and powers; no numerical package
is needed. Niagara slots, status flags and clock callbacks still need the Niagara adapter/API.

**Standalone Python example:** the next cell also runs as a plain Python 3.10+ script with `hvac_optimal/` available
on the import path. It imports no numerical or plotting package. The package supplies the complete tested BAS behavior;
copy/install that driver beside your script instead of replacing it with the two-line learning formula alone.
The original Java already uses scalar arithmetic; a Program Object port must preserve its surrounding behavior.
""")
code("""
from datetime import datetime
from hvac_optimal import Inputs, OptimizedStartStop

controller = OptimizedStartStop()
for clock, temperature, occupied in [('05:50:15', 66.0, False), ('06:00:15', 66.2, True)]:
    now = datetime.fromisoformat(f'2026-11-19T{clock}+00:00')
    next_event = now.replace(hour=18 if occupied else 6, minute=0, second=0)
    result = controller.tick(Inputs(
        space_temp=temperature, outside_temp=35.0,
        start_enable=True, stop_enable=True, schedule_status=occupied,
        next_event_time=next_event, next_event_value=not occupied,
    ), now=now)
    print(clock, 'heating minutes/degree:', result.state.runtime_per_degree_heating)
    for event in result.events:
        if event['type'] == 'native_learning':
            print('Native learning:', event['parameter'],
                  '| measured change:', event['temperature_change'],
                  '| full comfort reached:', event['target_reached'])
""", tags=['stdlib-controller'])
md("""
### Real BAS ventilation versus this simulator

During **verified-unoccupied** temperature recovery, the real BAS normally requests full recirculation by closing its
minimum outside-air damper position; occupied ventilation resumes at occupancy. Existing site ventilation, makeup-air,
pressurization and safety interlocks stay external to this algorithm. A damper position is not an outside-air flow measurement.

The competition simulator permits only **70% recirculation** while an AHU runs. Its maximum recirculation action cannot
test the real full-return-air case, so recovery/energy numbers here do not prove that operating condition. This note
does not change native learning eligibility or bypass site interlocks.
""")
md("""
## 4. What the PNNL models mean here

| Estimator | Main idea | Provenance / explicit adaptation |
| --- | --- | --- |
| M1 / Johnson | Quadratic gap plus initial response time | Supplied implementation subtracts the intercept before fitting curvature; printed paper differs. |
| M2 / Carrier | Learned rate with an outdoor-temperature ratio | Supplied code uses 0 °F heating reference; the paper prints 0 °C. No claim these are identical. |
| M3 / Siemens | Gap plus weather-load term | Preserve the supplied heating/cooling fit asymmetry. No fabricated signed arrival-feedback correction. |
| M4 / Sbs | Exponential error decay | Convert the fitted decay to minutes using actual sample intervals. |
| Median | Median of M1–M4 | Separate ordinary and post-weekend banks, not merely a label. |

`docs/model-provenance.md` identifies the supplied 2024-code hash, paper/deployment differences, original fitting checks
and the common-endpoint adaptation. The original PNNL notice is retained. Numerical requirements for fitting an estimator
do **not** add gates to the native BAS learner.

All replay predictors estimate first observed entry within **1 °F** of the target. Missing predictions stay missing;
unfinished observations stay partial/censored. There is no hidden 180-minute clipping of predictions.
""")
code("""
events = load_recovery_events(DATA, allowable_deviation=1.0)
print('Observed events:', len(events))
print(pd.Series([e['status'] for e in events]).value_counts().to_string())

# Research selection is outside the BAS reference. The chosen window and tie
# rule are explicit; only PAST common-cohort errors enter a decision.
selector = ResearchSelector(window=8, minimum_history=1, cold_start_model='native_minutes_per_degree')
result = run_replay(events, selector=selector)
summary = pd.DataFrame(result.summary()).set_index('model')
display(summary[['events', 'assessed', 'unassessed', 'common_assessed', 'common_mae', 'common_bias', 'fitted']].round(2))
""")
md("""
## 5. Compare accuracy **and** evidence

The left panel uses exactly the events assessed by every predictor. The right panel shows when a model has no scored
answer. Large errors remain visible; no hidden prediction cap makes a weak model appear accurate.

These are replay results on recorded controller trajectories. They do not establish the energy or comfort of a
different controller starting at another time. Old monthly CSVs changed stop algorithms between start arms and are
deliberately excluded from this comparison.
""")
code("""
plot_replay_summary(result)
plt.show()
plot_error_history(result)
plt.show()
""")
md("""
## 6. Shadow models and an explicit research champion

For each AHU: predict for all models, choose from **past** errors, observe the outcome, then train. Each heating/cooling
model keeps its own state; the weekend ensemble has its own bank. The default replay research choice is the simple native
minutes/degree predictor until prior assessed errors exist. The chart displays an actual decision history, not a
winner chosen after seeing that morning's outcome.

A lower time MAE alone does not guarantee lower energy, fewer late arrivals or better competition score. The selector
does not modify BAS eligibility. `ResearchOptimizedStartStop` is the separately named lead-prediction extension;
`OptimizedStartStop` remains the unchanged native-formula reference.
""")
code("""
plot_selection(result)
plt.show()
display(pd.DataFrame(result.selection_records).head(6)[['scenario', 'ahu', 'date', 'model', 'reason']])
""")
md("""
## 7. Run the actual competition simulator across every building

The runner discovers every `config.gin` in the attached official kit: the installed kit currently supplies **six buildings
and 30 scenarios**. Each AHU has independent controller and estimator state, plus its own fixed 30% zone sample and
selection receipt. All arms use the **same official PID-water plant controller**, schedule and opposite-phase policy.
`phase='start'` fixes scheduled stop; `phase='stop'` fixes scheduled start; `phase='both'` retains native optimal stop
while research arms change only start prediction.

The simulator's `winner` research policy falls back to the exact native command calculation when prior comparable
errors are unavailable. That command includes the original rounding and timing rules; the replay's native-rate
predictor is only an endpoint adapter, not the whole BAS controller.

The simulator has five-minute observations/actions. This adapter's decisions are quantized to that cadence; it is not
identical to Niagara's minute scans at :15. Geometry classification and any fallback are recorded per AHU.

**8640 steps** means a full 30-day episode. Short runs are integration smoke tests, never comparable competition scores.
Full runs can take hours. Results are resumable, job identities include source/config hashes, and output belongs in
a new TEMP directory locally or `/kaggle/working` on Kaggle. Attach the official simulator dataset separately; it is
not redistributed in this tutorial bundle. Locally, select the **HVAC Optimal Start Simulator** kernel. This cell
is enabled for the local notebook, so Run All includes the full simulator. Set it to False for just the quick tutorial.
""")
evidence_path = ROOT / 'docs' / 'validation' / '2026-11-18-simulation.json'
if evidence_path.is_file():
    evidence = json.loads(evidence_path.read_text(encoding='utf-8'))
    table = '\n'.join(
        f"| {row['building'].replace('building_train_', '')} | {row['native_mean_raw_reward']:.5f} | {row['winner_mean_raw_reward']:.5f} |"
        for row in evidence['buildings'])
    md(f"""
### What we actually ran

**{evidence['complete']} full 30-day jobs passed, zero failures:** six buildings, five weather cities,
30 scenarios, native and adaptive policies, {evidence['ahu_runs']} AHU-scenario runs.
All AHU instances recorded native learning. Every job ran 8,640 steps with its own fixed sample.

| Building | Native mean raw reward | Adaptive mean raw reward |
| --- | ---: | ---: |
{table}

Higher raw reward is better. Adaptive improved **{evidence['winner_better_scenarios']} of 30** scenarios and worsened
**{evidence['winner_worse_scenarios']}**. Native stays the default. This is one seed and local simulator reward,
not an official leaderboard result or proof of savings.

**The command objectives differ:** native commands target the full comfort boundary. Adaptive candidates predict the
1 °F arrival endpoint, with full-boundary native fallback when needed; the legacy G36 comparator adds its documented
margin. These are two configured policies, **not an isolated test of selector quality**. Common-endpoint MAE applies
to their shadow forecasts, not to these different commanded trajectories. A matched arrival-objective baseline is
still needed before attributing a reward difference solely to selection.

The retained summary is `docs/validation/2026-11-18-simulation.json`;
run signature `{evidence['run_signature']}`. Full traces remain outside the offline tutorial bundle.
""")

code(r"""
RUN_OFFICIAL_SIMULATOR = True
KIT = None  # Automatically discover this repository's .kit or an attached Kaggle kit.
POLICIES = ['native']  # add names from summary.index for matched research arms
STEPS = 8640          # shorter horizons are smoke tests only

if RUN_OFFICIAL_SIMULATOR:
    from hvac_optimal.simulation import discover_scenarios, run_matrix
    from hvac_optimal.simulator_setup import resolve_kit, preflight
    import tempfile
    KIT = resolve_kit(KIT)
    preflight()
    print('Simulator kit:', KIT)
    print('Python:', sys.executable)
    scenarios = discover_scenarios(KIT)
    display(pd.DataFrame(scenarios))
    output = (Path('/kaggle/working/optimal-start-stop-runs') if Path('/kaggle').exists()
              else Path(tempfile.mkdtemp(prefix='optimal-start-stop-runs-')))
    receipt = run_matrix(KIT, output, policies=tuple(POLICIES), steps=STEPS, workers=2,
                         phase='both', sample_fraction=.30, resume=True)
    display(pd.DataFrame(simulation_table(receipt)))
    print('Results saved to:', output)
    if receipt['failed']:
        errors = [job for job in receipt['results'] if job['status'] != 'complete']
        raise RuntimeError(f"{receipt['failed']} simulator jobs failed. First error: {errors[0].get('error', 'See receipt')}")
    completed = [job for job in receipt['results'] if job['status'] == 'complete']
    if completed:
        plot_ahu_trace(completed[0]['history_path'])
        plt.show()
else:
    print('Simulator disabled. Enable it explicitly after attaching the official kit and checking its dependencies.')
""")
md("""
## 8. The same driver behind an IoT adapter

No notebook is required at the edge. The standard-library driver accepts one timestamped JSON message per line and
returns command **values and statuses**, current learned parameters, sampling receipts and native learning events.
The external BAS adapter owns clock delivery, actual sensor validity and field writes; this tutorial performs none.
The example runs both start/stop paths without connecting to equipment. Configure station time explicitly in a real adapter.
""")
code("""
from hvac_optimal.iot import IoTDriver
edge = IoTDriver()
edge.process({'event': 'configure', 'device': 'AHU-example', 'zones': zones,
              'zone_types': zone_types, 'sample_fraction': .30, 'sample_seed': 7})
receipt = edge.process({'device': 'AHU-example', 'now': '2026-11-18T05:50:15Z',
    'zone_temperatures': {z: 66.0 for z in zones},
    'inputs': {'start_enable': True, 'stop_enable': True, 'schedule_status': False,
               'next_event_time': '2026-11-18T06:00:00Z', 'next_event_value': True}})
display(pd.DataFrame([receipt['state']['start_time_command'], receipt['state']['stop_time_command']],
                      index=['start command', 'stop command']))
""")
md("""
## 9. Reproduce, review, and contribute

- `python -m pytest -q` checks source-traceable native behavior, extracted-Java differential traces, estimator math,
  callback order, censored outcomes, AHU isolation, sampling and offline packaging.
- `python -m hvac_optimal replay --data data --out <TEMP>/replay` regenerates machine-readable replay receipts.
- `python -m hvac_optimal simulate --kit <official-kit> --out <TEMP>/matrix --steps 8640 --workers 2` runs all scenarios.
- `python -m hvac_optimal bundle --out <TEMP>/kaggle-bundle` builds the notebook's offline driver/data bundle.

Useful peer feedback: which paper/implementation equations should be compared separately; which observable comfort
endpoint is most useful; how selection behaves under changed climate; and whether matched full-length tests support
the same ranking. Keep native reference behavior and any proposed research change separately identified.

References: Kim et al., *Applied Thermal Engineering* 257 (2024), 124256,
https://doi.org/10.1016/j.applthermaleng.2024.124256 ; supplied PNNL implementation and its retained notice;
https://github.com/smart-buildings-2026/starter-kit ; `docs/reference-contract.md`, `docs/model-provenance.md`,
`docs/datasets.md`, `docs/sampling.md` and `docs/simulator.md` in the source repository.

The supplied decompiled Java is not included in the Kaggle dataset. This is a local educational build; no upload or
competition submission has been performed. The Python driver is not a claim of Niagara-runtime or field certification.
""")

notebook = nbf.v4.new_notebook(cells=cells, metadata={
    "kernelspec": {"display_name": "HVAC Optimal Start Simulator", "language": "python", "name": "hvac-optimal-sim"},
    "language_info": {"name": "python"},
})
nbf.write(notebook, ROOT / "optimal_start_stop_tutorial.ipynb")
print(f"Generated {len(cells)} cells; implementations remain in hvac_optimal/.")
