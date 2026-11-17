# Closed-loop benchmark on the NeurIPS 2026 Smart Buildings simulator

This harness ran every start and stop algorithm in `hvac_optimal`, plus the neurips
repo's own controllers, in the competition's building simulator. It produced the tables
in the top-level README.

## What a run is

* **One scenario** = one competition building (`building_train_{1,2,4,5,7,8}`) with one
  30-day weather strip, simulated in 5-minute steps (8640 steps). It has 4–9 AHUs and
  39–150+ VAV zones with reheat. The occupied band is 294–297 K, 06:00–19:00, and
  occupancy is randomized.
* **One run** = one start algorithm on every AHU, plus one stop algorithm.
* **The plant is the same for every hooked arm.** The G36 sequence from the neurips repo
  (`sac_trim/g36_backbone.py`, v6 compatibility mode) controls supply air, static
  pressure, reheat and night setback. The harness swaps only two decisions:
  *when the AHU commits to warm-up/cool-down* (start) and *whether it may shut off before
  the end of occupancy* (stop). It does this through two hooks patched into an
  in-memory copy of the backbone, so the neurips repo is never modified.
* **Native arms** run the neurips controller unchanged, including its own plant control:
  * `v6`: the backbone's own learned-rate start (×1.25 safety, +15 min, 120 min cap) and
    its own stop (recovery-rate drift proxy).
  * `v7`: `G36HighSatPolicy` default mode (RecoveryLearner + occupancy trees).
  * `sac_trim`: the SAC residual policy with `results/sac_trim/run1/best_actor.json`.
  * `sac_full` is not run separately: with its zero actor it is bit-for-bit v7. The DQN
    controller exists only as a spec, so there is nothing to run.
* **Learning is online only.** Every learning model starts empty on day 1 of every run.
  It learns only from recoveries and coasts it has already seen in that run. Nothing
  learns from the future, and nothing is shared between runs. The first 7 days are
  excluded from the scored metrics as warm-up, though they are still simulated and learned
  from.

## Reproduce

```powershell
# 1. Use the neurips repo venv (it has the simulator). Point at its kit:
$env:SMART_BUILDINGS_KIT = "C:\path\to\neurips-2026-smart-buildings\.kit"
$py = "C:\path\to\neurips-2026-smart-buildings\.venv-sim\Scripts\python.exe"

# 2. (optional) Generate the unseen Minneapolis scenarios. These are not in the training
#    set, so they also give a leakage-free test of the trained SAC actor:
cd $env:SMART_BUILDINGS_KIT\smart_buildings
& $py run_scenario_generator.py --weathers minneapolis_1 minneapolis_6 --output-dir $env:TEMP\osbench\scenarios

# 3. Write a job list (scenario x start; stop algorithms rotate across start arms):
cd <this repo>\benchmarks\neurips_sim
$tr = "$env:SMART_BUILDINGS_KIT\smart_buildings\training_scenarios"
& $py make_jobs.py --scenarios $tr\building_train_1\fairbanks_1 $tr\building_train_2\denver_8 `
    --outdir results\phase1 --out jobs.json

# 4. Run them (resumable; create a file named STOP here to drain the queue):
& $py run_queue.py --jobs jobs.json --neurips-root C:\path\to\neurips-2026-smart-buildings `
    --workers 8 --actor C:\path\to\neurips-2026-smart-buildings\results\sac_trim\run1\best_actor.json

# 5. Metrics and tables (numpy + pandas):
& $py analyze.py results\phase1 --out results\analysis
```

One 30-day run takes about 5 min on one free core, or about 18 min each with 8 in
parallel on an 8-core desktop (the simulator is memory-bandwidth bound).

## Metrics (see the `analyze.py` docstring for exact definitions)

| metric | meaning |
|---|---|
| lead | minutes of warm-up (start committed) before occupancy |
| late % / late p90 | share of AHU-days on which a recoverable zone was still out of band at occupancy, and the 90th-percentile delay |
| early waste | minutes all recoverable zones sat in band before occupancy while the AHU was already in warm-up |
| unmet K·min/zone | band deficit summed over the first 2 h of occupancy (degree-minutes; 1 K = 1.8 °F) |
| unmet w/ people | the same over the first 3 h, counted only while occupants are in the building |
| energy saved vs fixed_120 | electricity + gas cost from 4 h before to 2 h after occupancy start, paired with the `fixed_120` run on the same scenario-day |
| reward gain | the simulator's own reward (productivity regret + energy + carbon) over the same window, paired with the same baseline |
| stop: early-stop min, restarts, unmet, max excursion | over the last 3 h of occupancy, paired against `no_early_stop` |

Capacity-limited zones never reach the band on some days (Fairbanks in January is the
clearest case). No start time can fix them, so they are left out of the arrival timing
but still count in unmet degree-minutes.
