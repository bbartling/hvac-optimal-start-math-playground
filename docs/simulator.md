# Official simulator adapter

`hvac_optimal.simulation` discovers the checked-out official starter kit's actual
`smart_buildings/training_scenarios/*/*/config.gin` files. It does not infer a
scenario matrix from weather names. The supplied checkout contains 30 scenarios
across six buildings and five weather stations. `discover_scenarios(kit)` is a
standard-library-only inventory operation. Simulator imports happen only when
running jobs, using the separately installed official simulator dependencies.

```python
from hvac_optimal.simulation import discover_scenarios, run_matrix

scenarios = discover_scenarios(kit)
smoke = run_matrix(kit, new_output_directory, policies=("native",),
                   steps=12, workers=2, phase="both", sample_fraction=0.3)
# A separate directory is required for a full matched horizon:
full = run_matrix(kit, another_new_directory, policies=("native", "winner"),
                  steps=8640, workers=2, phase="start")
```

On Windows, call multiprocessing entry points from a guarded `if __name__ ==
"__main__":` or the provided CLI. Use the simulator's Python environment; the
core package deliberately does not install the simulator as a mandatory
dependency. The adapter writes generated Gin wrappers and caches under TEMP;
metrics are disabled before environment construction/reset. It rewrites input
paths to absolute paths and never changes the sibling kit, its controller, its
scenario files or its results. Geometry inputs are preflighted as numeric 2D
arrays with `numpy.load(..., allow_pickle=False)` before the upstream loader.

## Matched control arms

Every arm uses the same official `PIDWaterResetPolicy` air/water control and the
same schedule. This adapter adds explicit schedule/run-command handling around
that common plant; this is not the vendor's plant sequence. Outside schedule an
AHU runs only under a non-null true start override. A non-null false stop
override disables its AHU. Unselected AHUs and their zone actuators are masked;
water pumping is shared by the remaining running handlers. Occupied/prestart
comfort bands are supplied to the unchanged PID; the actual schedule object's
`is_comfort_mode` result controls the choice, including holidays. Input AHU
heating/cooling mode latches the previous signed PID error, initially heating;
this external mode adapter is recorded in the tick logs.

`native` uses the frozen optimal-start **and** optimal-stop port. Other arms
replace only the start prediction through `ResearchOptimizedStartStop`; stop
prediction always returns the native lead. Unsupported candidate predictions
explicitly fall back to native. No rate bounds, 180-minute cap, sample minimum,
temperature-change minimum or new native learning restriction is introduced.

For `phase="start"`, all arms disable early stop and use scheduled stop. For
`phase="stop"`, all arms disable early start and use scheduled start; the current
research estimators have no alternative stop algorithm. For `phase="both"`,
all arms enable start and stop, holding the native stop rule fixed while start
prediction varies. These phases must not be combined as one score cohort.

The supplied simulator advances every **300 seconds**. Native calculations are
quantized to those observation/action opportunities. This does not reproduce
Niagara's minute cadence offset 15 seconds after the minute. The adapter uses the
schedule object's own timestamp-localization convention for both current and
next-event timestamps; naive timestamps in this kit are interpreted by that
object as UTC. Logs expose the configured timezone, effective schedule timezone
and whether schedule inputs were naive. It does not silently repair the kit's
schedule implementation.

## Independent AHUs and representative input

Each AHU owns a fresh native controller, eight research estimators, prediction
histories and a fixed `ZoneSampler`. The default samples `ceil(0.3 * zone_count)`
zones with counts as evenly split between exterior and interior as available
classification permits. Default averaging uses **equal weights**. Explicit
`zone_weights={ahu_id: {zone_id: positive_weight}}` can represent a configured BAS
weighting; geometry cell counts are never automatic weights.

AHU-to-zone and zone-to-VAV relationships come from the simulator's actual HVAC
metadata. Exterior/interior classification uses each mapped room's coordinates
and adjacency to the simulator's processed exterior-wall mask; IDs are lookup
keys, not classification heuristics. Receipts include every selected/mapped ID,
weights, classification counts, adjacency evidence, actual sample fraction,
balance and unknown/fallback details. Actual zone readings are denormalized from
the official observation metadata, converted from Kelvin to Fahrenheit, then
averaged within that AHU. Native coefficients remain minutes per Fahrenheit
degree. Each scenario/policy starts from independent state.

## Predictions, native observations and assessment

Start-trigger predictions are frozen before outcomes and fitting. Research MAE
uses the first **observed** sample within 1°F of the comfort boundary, with no
interpolation. Endpoint tracking continues after a partial native observation
at occupancy; it ends at the endpoint, next scheduled unoccupancy or run
horizon. The final observation actually returned by the last `env.step` is
included in research assessment. It does not cause an additional native tick,
native learning update or plant action; a final-step crossing is observed rather
than falsely censored. The original native learner still updates exactly when its own
eligibility conditions hold. This research window and the recorded-recovery
replay are separate data-generation processes even though the endpoint matches.

The research fit event retains the full observed native-eligible trajectory;
the scoring trace truncates at the common 1°F endpoint. Every estimator receives
an explicit receipt for the native-eligible episode. A model that accepts that
partial fit is updated once. A model that rejects it can receive one explicitly
logged deferred research fit when the endpoint is later observed; this neither
repeats nor changes the native update. No native-eligible episode is invented
when the run ends without one.

Own-support MAEs are diagnostic and show assessed, unassessed and unsupported
counts. `common_assessed` and `common_mae_minutes` use the identical completed
episodes where all research candidates had a prediction. The `winner` arm
reuses `replay.ResearchSelector`: last eight common errors, separate heating /
cooling and post-weekend histories, one observation required, insertion-order
ties, and explicit native fallback when no eligible history exists. These are
research selector rules, not native BAS guards. Histories never cross AHUs,
scenarios or policy jobs.

`native_endpoint_adapter` is a derived shadow forecast to the 1°F research
endpoint. It is **not** the frozen native command lead, which targets the full
comfort boundary and remains visible in controller state and prediction logs.
Neither shadow prediction MAE nor short-run reward establishes a counterfactual
energy saving or official leaderboard performance.

## Ventilation boundary

For verified-unoccupied recovery, the real BAS convention requests full
recirculation / a closed minimum outside-air damper position, restoring occupied
ventilation at occupancy. A minimum damper command does not guarantee a measured
outside-air flow; existing site interlocks remain external to this algorithm.

The adapter requests maximum recirculation during native prestart. The official
simulator's `AirHandler` caps actual recirculation at **70%**, so it still draws
at least 30% outside air while running. Its maximum command cannot reproduce
full-return-air prestart. Each job receipt records that cap. There is no claim
that 100% recirculation occurred, or that the measured recovery/energy result
transfers to that real operating condition.

## Receipts and resume

`run_matrix` returns a manifest dictionary with numeric `complete`, `failed` and
`pending` counts. It records code, native source, kit code/data, parameters,
policy, sampling and actual step count. Resume accepts only the same signature
and complete requested step count plus an intact history artifact with matching
SHA-256. Different code/config/steps require a new
output directory, so twelve-step smoke tests cannot be mistaken for 8,640-step
scores. Unknown existing files are never overwritten. Failed/incomplete jobs
restart in a new attempt directory, retaining the earlier attempt.

Each attempt contains an atomic `receipt.json` and `ahu.jsonl.gz`: job metadata,
sampling/classification, every AHU tick and coefficient/output state, native
events, predictions, endpoint outcomes and fit receipts. The manifest is
updated atomically as jobs complete. A completed short run is labeled
`integration_only_not_a_competition_score`; a full 8,640-step run reports local
raw reward without pretending that it is an official submission result.
