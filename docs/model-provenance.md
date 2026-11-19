# Estimator provenance and common assessment endpoint

`hvac_optimal/models.py` is a set of standalone, standard-library research
estimators. These classes do not replace the frozen BAS start/stop driver in
`hvac_optimal/reference.py`. They do not change its checks, four native parameter
states, schedule transitions, latches, or eligibility for partial learning.

## Supplied research source

The owner supplied `optimal_start_models.py`, 607 lines, carrying a 2024 Battelle
Memorial Institute notice. Its SHA-256 is
`8443c449ee77f34a21fa5577c600e1d6307363a23cf30cac7d7a39427085c322`.
The original notice is retained in the adapted module and
`LICENSES/PNNL-BSD.txt`. The external dependencies and framework integration in
that file are not required by this event-based implementation. Its debug CSV
writes (`sort.csv`, `sort1.csv`, `htr.csv`) are not reproduced.

The paper is Kim, Yu, Lutes and Katipamula, *Implementation and validation of
optimal start control strategy for air conditioners and heat pumps*, Applied
Thermal Engineering 257 (2024), 124256,
[DOI](https://doi.org/10.1016/j.applthermaleng.2024.124256). A copy is included in
`PNNL_Paper/`. The supplied source and paper are separate evidence: their
equations and behaviors are not identical.

The source imports helper functions and configuration that were not in the
supplied file. This package therefore does not claim a literal port of its full
dataframe preprocessing. It receives measured recovery events from a separate
driver. Its first-degree time uses linear interpolation between adjacent
timestamped samples. It does not reconstruct the source's quarter-degree
heat-transfer table, fan/conditioning filters, schedule window, or resampling.
Those are input preparation, not newly invented BAS learning restrictions.

The finite-window weighting helper is explicitly the algorithm in the later
[AEMS utils.py, pinned at 7c65251](https://github.com/VOLTTRON/volttron-pnnl-aems/blob/7c65251ea9b730e0a6ea1fec594c8989c1767f22/aems-edge/Manager/manager/utils.py#L199-L217):
weight `min(1, 4/(n+1))`, initialized with the oldest stored coefficient.
The default 8-event history is a configuration choice consistent with that
later implementation, not the paper's 10-weekday training window. Later AEMS
code is used only where explicitly identified here; it is not substituted for
the supplied 2024 model definitions.

## One endpoint for fitting, predictions and scoring

Temperatures are in Fahrenheit and elapsed times in minutes. `target` is the
selected occupied heating or cooling comfort boundary. With configurable
`allowable_deviation = d` (default 1 F), assessment is complete at `target-d`
while heating or `target+d` while cooling. The required change is therefore
`max(initial distance outside the boundary - d, 0)`.

Predictions use that required change. Model 1's quadratic denominator and Model
3's residual weather formula retain their initial-gap structure with this
required change substituted for the full initial gap. Carrier, the linear EMA
and the native MPD adapter fit actual observed temperature change divided by
actual elapsed time (or its inverse for MPD), including partial observations.
Event `t` measures time to the common endpoint for assessment; a missing `t`
does not erase measured partial response evidence. This is an intentional
common-endpoint prediction adaptation. The supplied Johnson,
Carrier and Siemens prediction equations use the full boundary gap after their
tolerance check; reproducing that behavior literally would give a different
assessment endpoint from the Sbs logarithmic tolerance prediction. Setting
`allowable_deviation=0` gives the literal full-gap algebra for Models 1-3.
Model 4 requires a positive deviation because exact arrival at an exponential
asymptote has no finite solution.

The nominal occupied boundary still determines Model 3's outdoor load term.
Start-time caps, schedule limits and equipment commands belong to the driver.
Candidate classes return raw response-time predictions; at the common endpoint
they return zero. This differs from the source's 10-minute minimum start and
Sbs's internal start-time clipping. An undefined or negative mathematical
prediction returns `None` with `last_prediction_reason`; the driver exposes its
fallback choice. Carrier ratios are not silently clipped into a plausible range.

## Model-by-model choices

| Class | Supplied code and paper relationship | Event adaptation |
|---|---|---|
| `PNNLModel1` | Johnson uses `a=(t-b)/gap^2`, with `t/(10*change)` fallback when `t-b<1`, and `b` the first-degree time. Paper Eqs.12-14 instead print `a=t/gap^2`. | Preserve the supplied subtraction, fallback and positive finite coefficient checks. Use the common required initial gap in the quadratic denominator and actual observed change in the fallback. First-degree elapsed time is interpolated from the measured trace. Available partial intervals are eligible if these coefficients can be identified. |
| `PNNLModel2` | Carrier uses the ratio `(reference-previous OAT)/(reference-current OAT)`. Supplied heating reference is **0 F**, cooling **100 F**. Paper p.4 specifies **0 C = 32 F** for heating. | Default to the supplied 0 F constant and label it. `oat_ref_heat=32` is available for explicitly named paper-constant experiments. Fit actual observed change/time, including any positive partial response, and store event mean OAT. Report singular ratios and nonphysical negative predictions instead of the old notebook's added ratio clamp. |
| `PNNLModel3` | Supplied Siemens cooling fits the first coefficient from the **observed-interval average**, while heating uses the **first degree**. Both solve a residual outdoor coefficient and clamp a nonpositive second coefficient to zero. Its `adjust_time` starts at zero and is **never updated**. Paper Eqs.18-20 describe a different identification procedure, closed-damper condition, and arrival adjustment. | Preserve the supplied heating/cooling asymmetry and zero adjustment. Heating needs an observed first degree; cooling can fit a subdegree partial rate because its first-degree result is unused. Store coefficients in minutes rather than source hours, canceling the source's final factor of 60. Do not invent arrival feedback or infer negative overshoot from nonnegative deficits. |
| `PNNLModel4` | Sbs estimates the lag-one error factor with least squares, bounds it to `[.001,.999]`, and predicts `log(deviation/initial_error)/log(factor)`. | Fixed-cadence fits convert the factor to **per minute** with `factor^(1/dt)`. Irregular cadence uses least squares of `e_next=e_previous*exp(-lambda*actual_dt)`. Do not apply the per-sample bound a second time after conversion. Reset the lag at each event; the supplied file retains `e_last` across batches. Keep separate heat/cool histories rather than the source's shared alpha. |

For irregular-cadence Model 4 fitting, the source per-sample bounds are translated
to decay-constant bounds using the observed mean interval. A bounded scalar
least-squares fit uses the actual interval of every pair, with no assumption
that an average interval makes irregular pairs equally spaced. This is a
documented numerical adaptation, not a new BAS event eligibility check.

`PNNLMedian` is an explicitly assembled ensemble, not a fifth paper model.
The paper p.18 proposes separate Monday/holiday treatment as future work; it
does not describe median selection as its field comparison. The later
[AEMS manager, pinned at 7c65251](https://github.com/VOLTTRON/volttron-pnnl-aems/blob/7c65251ea9b730e0a6ea1fec594c8989c1767f22/aems-edge/Manager/manager/optimal_start_manager.py#L483-L562)
does use a median and distinct post-weekend/holiday model banks. Here the
ordinary bank stores 8 events per mode and the post-weekend bank stores 4.
Only the selected bank is trained. Until that bank has an accepted fit, a
post-weekend prediction uses the ordinary bank. An untrained constituent
contributes the explicit `cold_start_lead` (180 minutes by default). Missing
weekend flags are ordinary events; no calendar meaning is guessed by a model.

## Comparison estimators and the native driver

`LinearRateEMA` learns degrees/minute from measured full or partial responses,
with default weight .2. `G36RecoveryLearner` is a **G36-inspired legacy comparison**, using a
per-interval rate EMA, a 1.25 multiplier, a 15-minute buffer and 120-minute cap.
It is neither an official Guideline 36 definition nor proof of competition
controller equivalence. Both have the same assessment endpoint as Models 1-4.

`NativeMinutesPerDegree` is a **research endpoint adapter** of the Java start
learner's parameter weighting, not a replacement or behavioral port of
`BOptimizedStartStop.java`. The Java default `oldParameterMultiplier=2` implies
`new=(2*old+observed)/3`, so its default `alpha` is 1/3. Its default parameter
prior is 10 minutes/degree, as configured for the owner's native baseline.
A caller may explicitly configure another prior for a separately labeled experiment.
This offline adapter keeps heat/cool start-response values, whereas the frozen
reference has four independent start/stop learners, Java numeric behavior,
Niagara status distinctions, reset ordering, schedules and latches.

Native adapter fitting uses actual measured elapsed time divided by actual
directional temperature change. It accepts any positive correct-direction
partial response, including 0.001 F and a single timestamped observation
paired with the event's measured start. It does not impose a sample minimum,
minimum change, tolerance-sized change, epsilon floor, outlier rejection or
completed-recovery requirement. The common endpoint changes its *prediction*
assessment, not the eligibility of an observation already supplied by the
native harness. Whole-recovery candidate models' need for a measured endpoint
and model-specific coefficient checks do not govern native BAS learning.

## Event API and training evidence

Every model implements:

```python
prediction = model.predict(mode, temp, target, oat, post_weekend=False)
receipt = model.update({
    "mode": "heat", "start": 65.0, "target": 70.0,
    "oat": 30.0, "oat_mean": 31.0,
    "t": 40.0, "complete": True,
    "traj": [(0.0, 65.0), (5.0, 66.0), (40.0, 69.0)],
    "arrival_error": None, "post_weekend": False,
})
receipt.as_dict()  # JSON-compatible accepted/rejected result and fitted values
```

`mode` is `heat` or `cool`; prediction precedes observation and update. `t=None`
or `complete=False` censors the target-duration label, independently of whether
the observed response supports a rate or model-specific curve fit. `arrival_error` is signed observed temperature error or
`None`; these source-derived Siemens models do not use it. No overshoot is
invented when a trace ends at first endpoint arrival.

Chronology is never repaired by sorting. Duplicate, reversed, negative or
nonfinite elapsed coordinates return an `invalid_trajectory` receipt. A
trajectory iterable must describe the event from its measured start and may
contain nonmonotonic temperatures; warming/cooling is not assumed from order.
An independent replay groups each zone and hardware context in chronological
order. The model API itself has no clock or access to future events.

Trajectory iterables are materialized once before validation and fitting, so
generators have the same meaning as lists. A missing outdoor temperature only
prevents weather-dependent Models 2 and 3 from predicting. Models 1 and 4 and
the non-weather comparisons do not acquire an artificial outdoor-sensor
requirement. These candidate input/fit receipts never alter native reference
learning eligibility or statuses.

Tests include source-algebra hand calculations with zero tolerance for Models
1-3; common-endpoint heat/cool checks; exact known exponential curves with
regular and jittered timestamps; source coefficient constraints and visible
rejections; independent weekend banks; and tiny partial native observations.
These are estimator and integration checks, not field validation or a matched
30-day competition experiment.

## Partial response evidence and deferred fitting

The supplied Carrier, Johnson and Siemens training routines do **not** require
a completed comfort recovery. Their later available `get_time_temp_diff` helper
returns the elapsed observation window and actual directional temperature
change; its target-based filter is commented out. Carrier rejects a nonfinite
or nonpositive observed rate. Johnson also requires a positive first-degree
coefficient. Siemens heating requires its positive first-degree coefficient;
cooling uses the observed average and can fit when the first degree was not
reached. No generic `complete=True` gate is imposed in this implementation.

Carrier and the local linear EMA accept a 0.001 F correct-direction partial
response without a minimum-change floor or a sample-count requirement. Their
receipts state `fit_quantity="observed_rate"`, actual elapsed/change values,
`complete=False`, and `target_duration_inferred=False`. This is rate evidence,
not a measured full time to comfort and not an assessed MAE outcome.

Johnson and Siemens retain the supplied fit structure: observed interval time
enters formulas that also use the initial required gap. When those source
conditions permit a partial fit, the receipt says `fitted_partial_curve` and
`fit_quantity="observed_interval_coefficients"`; it never invents a completed
target duration. In particular, a Johnson fit from a short partial interval can
understate the time required for the whole gap because of its inherited
initial-gap denominator. This source behavior is visible rather than repaired
by an added full-recovery requirement. The stated common-endpoint adaptation
and such partial-interval bias must be distinguished from literal paper fits.

`retry_rejected(event, previous_receipt)` is explicitly a **research data-flow
operation** for the same earlier native-eligible episode when more curve
evidence arrives later. Accepted fits are never repeated. A median ensemble
retries each rejected constituent separately, preserving already accepted
Carrier/Sbs or other constituent fits. The returned `accepted` flag counts only
a new fit; `details.episode_fit_accepted` retains cumulative episode status so
repeated retries cannot duplicate an earlier accepted fit. Callers pass the
latest receipt onward, maintain episode identity, and log the original native
eligibility time separately from the later fit time.

Deferred fitting never calls the frozen Java reference learner, generates a new
native learning event, or changes its eligibility checks, coefficients or
latches. Native training happens once at its original eligible observation.
Independent outcome assessment can continue after that partial observation,
and a later complete research label can support only previously rejected
candidate fits. Prediction, observation, fitting and assessment timestamps
remain separate evidence.
