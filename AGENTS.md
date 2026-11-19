# Agent contract: optimal start AND stop

Work in this repository; disposable source/evaluation copies belong only in Windows TEMP. Read `docs/reference-contract.md` and the applicable source provenance before changing control code. Do not change the sibling competition controller or its active jobs. Never publish/submit to Kaggle or write to field equipment as part of local testing.

## Frozen BAS behavior

`hvac_optimal/reference.py` ports the supplied `BOptimizedStartStop.java` as a behavioral reference for BOTH optimal start and optimal stop. Preserve its checks, execution order, four independent minutes-per-degree learners, parameter weighting, schedule/time boundaries, latches, numeric behavior and output value/status distinctions.

Do not add sample minimums, temperature-change minimums, epsilon guards, rate clamps, cooldowns, confirmation timers, outlier rejection, occupancy checks or training restrictions absent from the reference. In particular, a small correct-direction response at the schedule transition is an eligible partial learning observation in the supplied code. Do not suppress that update. Document surprising source behavior rather than silently fix it.

Any intentional difference must be a separately named research extension, with explicit provenance and tests. Candidate estimator fitting constraints are separate from native BAS learning eligibility. Model ranking and switching never modify the frozen reference defaults or secretly alter native state/reset logic.

The reference file is an industry BAS implementation supplied by the owner. Its age, field history and external interlocks have not been independently established here. Do not claim a Python translation is field-validated or proven equivalent to the Niagara runtime from source inspection alone. State which checks compare extracted Java control code and which framework semantics are emulated.

## Evidence

Keep paper equations, supplied PNNL research code, later deployed implementations and local adaptations distinct. Preserve applicable attribution/license notices. Predictions must precede outcomes and training; metrics need a common endpoint and visible censored/unassessed counts. Start comparisons hold stop/plant/schedule fixed; stop comparisons hold start fixed. Do not reuse the old confounded score tables as new validation.

The core driver and estimators must import with the Python standard library alone. Notebook/data/plot dependencies are optional. Package all code/data needed for an offline Kaggle tutorial; do not depend on a moving GitHub download. Short simulator runs prove integration only; competition score claims require the full matched horizon.

## Real AHU input and ventilation context

Each AHU has independent controller/learner state. The owner's representative-temperature convention is a configurable zone sample, currently 30% by default, split as evenly as available metadata permits between exterior and interior zones. Keep the selected zones fixed during a run, average only that AHU's mapped sensors, and report selection, weights, classification source and any unknown-class fallback. Do not guess perimeter/interior status from point names or change the native learning gates because sampling is used.

For verified-unoccupied temperature recovery, the real BAS sequence normally requests full recirculation / closed outside-air minimum (often called minimum outside-air damper position). Restore the occupied ventilation sequence at occupancy. Minimum damper position is a command, not a guaranteed outdoor-air flow measurement. Existing site ventilation, makeup-air/pressurization and safety interlocks remain outside this algorithm; this note does not authorize bypassing them or add a new learning restriction.

The competition simulator caps recirculation at 70% when an AHU runs. A maximum recirculation action therefore cannot reproduce a real system's full-return-air prestart. State this limitation in the notebook and simulation receipts; do not claim 100% recirculation or generalize its energy/recovery results to that operating condition. These are plant-adapter semantics, not alterations to the supplied start/stop state machines.

Run the source-traceable reference fixtures, Java differential tests where available, estimator analytic tests, prequential replay tests, IoT JSONL tests, artifact/offline import checks and full notebook execution. Report actual datasets/scenarios run and distinguish planned experiments. Checkpoint and locally commit coherent work before the requested quota sleep; do not push without a task instruction to publish.
