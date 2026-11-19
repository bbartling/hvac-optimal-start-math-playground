# Dataset inventory and assessment endpoints

`hvac_optimal.datasets.inventory_datasets(path)` scans candidate CSV/CSV.GZ,
JSON/JSONL, NPZ/NPY, Parquet and Gin files under the supplied root, including
hidden `.kit` simulator inputs. Counts are discovered from the filesystem. Git
internals, dependency environments, source code and tool caches are excluded.
Every candidate receives a classification, usability decision and reason;
inspection errors remain visible. Numpy headers are inspected with the standard
library, without loading array payloads or unpickling objects. Inventory is
read-only and does not run the simulator or contact the network.

The notebook can inventory the sibling `neurips-2026-smart-buildings` checkout
when available. It remains optional for an offline Kaggle run: the bundled
recovery CSV files supply the tutorial's measured event replay. The sibling's
contents are local artifacts, not an independently collected field dataset.

| Artifact | What it supports | What it cannot establish |
|---|---|---|
| Paired `recovery_events.csv.gz` and `recovery_traces.csv.gz` | Recorded simulator zone temperatures in °F, elapsed minutes, declared target and OAT; prequential prediction tests | New start schedules' closed-loop energy, comfort or competition score |
| Scenario `config.gin`, `floor_plan.npy`, `zone_map.npy` | Inputs for fresh official-simulator experiments | Measured warm-up durations |
| Weather CSVs | Outdoor weather, using explicitly named temperature/time columns | Zone recovery or HVAC response |
| RL chunk NPZs with `feats`, `acts`, `rews`, `score`, `steps` | Policy-training arrays and aggregate rewards | Raw physical zone temperature, stable zone identity, schedule or target-time truth |
| Actor/snapshot JSON | Learned weights and feature normalization | Its generating temperature histories |
| Episode JSONL and evaluation/result JSON | Episode scores and run metadata | Per-zone start/stop outcomes |
| Archived `synthetic_recovery_events.csv` | Synthetic °F temperature changes with UTC timestamps; illustrative rate observations | Comfort arrival time: targets, setpoints and OAT are absent |
| Old start/stop result CSVs | Diagnostic examination of the old experiment | New validation: start arms mixed stop algorithms, and native v7 also changed other control logic |

An unrecognized schema or a file with unknown units is reported as unusable for
recovery assessment. The inventory never reverses normalized RL features into
invented physical temperatures. A potential physical trace with `tz/oat/ts`
arrays is reported as needing an explicit units/schedule/zone/controller adapter.

The local sibling snapshot inspected on 2026-11-18 contained 288 candidate data
files: 30 training scenarios with 60 geometry arrays, one evaluation copy with
two geometry arrays, 121 RL chunk NPZs, 56 JSON files (41 under `results/`), two
episode JSONLs, 12 weather CSVs, one synthetic rate-history CSV, two aggregate
benchmark CSVs and one submission Parquet. The episode logs had 221 and two
records. The synthetic temperature file had 72 rows; the aggregate benchmark
files had 40 and 32 rows. All 121 NPZs had the RL feature/action/reward schema;
no physical recovery archive was discovered there. These are reported inventory
findings, not constants in the discovery code or evidence of running 30 scenarios.
The submission Parquet is explicitly uninspected by the stdlib inventory.

## Common endpoint and all-event replay

`load_recovery_events(data_dir, allowable_deviation=1.0)` returns **all 1,163**
bundled events. These counts describe the bundled snapshot; inventory code does
not assume them. The original exact-target label has 130 censored recoveries.
With the declared 1 °F assessment tolerance, 1,090 events have an observed
endpoint, including 298 already within tolerance at the recorded start. The
remaining 73 lack a full endpoint label. Censored events remain in the result
with their actual measured partial trajectory and training receipts.

The endpoint is the **first observed sample** within `target ± tolerance` in the
conditioning direction. No time is fabricated beyond the observed trajectory,
and there is no interpolation of assessment time. Model fitting may separately
interpolate its first one-degree crossing; its receipt documents that estimator
operation. Predictions use the initial distance minus tolerance as the required
change. Fitting follows each estimator's documented source equations and can
use measured partial responses without a completed endpoint label. The native
minutes-per-degree research adapter uses actual observed directional change,
including arbitrarily small positive partial responses. Fit receipts expose
which measured quantities and eligibility conditions were used.

`source_complete` and `source_minutes_to_target` retain the old exact-target
label. `complete`, `t` and `status` describe the new common assessment endpoint.
A partial positive response is not a completed target duration. At-endpoint
events have a real observed duration of zero; they are not converted into a
positive fitting duration. Invalid/missing/unordered traces are visible and
never train candidates. Trace order is checked, not repaired from future data.

## Causality, missing predictions and selection

`run_replay(events)` creates fresh estimators for every scenario/AHU and orders
events by recorded date. Every candidate predicts from the initial state before
the current outcome is assessed or any candidate trains. Copies isolate
callbacks and candidates from one another. Mode and post-weekend error histories
are separate; ensemble estimators own their explicitly separate training banks.
No global pre-fit or cross-scenario learning occurs.

Missing predictions stay missing. There is no default maximum-lead clamp,
imputed 180-minute cold-start prediction, or hidden controller guard. An
explicit `max_lead=` research experiment retains both the raw and capped values.
Summary rows show all-event counts, original and endpoint censoring, unavailable
predictions, fitting reasons, and assessed/unassessed counts. Per-model available
cohorts are diagnostic; compare candidates using the **common assessed cohort**,
where all candidates supplied a prediction for the same completed endpoint.

`ResearchSelector` is an explicitly named alternative to native BAS behavior.
It selects the lowest prior MAE on shared, completed history in the same
scenario/AHU/mode/post-weekend group. Window length, minimum history and an
optional cold-start model are public arguments. Ties use candidate insertion
order. Without qualifying history there is no selection by default. It has no
native-control hooks, coefficient guards or safety claims. Selection callbacks
are emitted before the current outcome; error-history records make later model
switches reviewable.

Replay measures prediction on the recorded fixed-180 policy's initial states.
It does not show what would have happened had a different policy started the
plant later, because the initial thermal state and subsequent plant trajectory
would change. Fresh matched simulator experiments are a separate workflow.
