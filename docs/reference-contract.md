# Supplied BAS reference contract

`hvac_optimal.reference` is a local behavioral translation of the owner-supplied
`BOptimizedStartStop.java`, for optimal start **and** optimal stop. The original
decompiled proprietary source remains outside this repository. Its SHA-256 is
`0F2B759951F18DEC2BA05C09D8B03569C90C0D69B3BB08CC18FFB9009FE3A539`.
Source line references below identify that 945-line file, not a public release.

The reference preserves surprising behavior rather than adding protections.
It is not a claim of field validation of Python, certification against Niagara,
or independent verification of the supplied implementation's age or history.

## Preserved contract

The Java tick order is reset `startDone`, analyze using the previous mode,
calculate, control, update output statuses, remember mode (706–716). Modes are
0 none, 1 start calculation, 2 start in process, 3 stop calculation, and 4 stop
in process (938–942). Cooling is true; heating is false (935–936).

Start eligibility requires enabled start and inactive schedule. New prediction
also requires valid space temperature and an unset `startDone` latch (733–747).
Outside the inclusive comfort band, lead minutes are `1 + int(gap * minutes /
degree)`; inside the band lead is zero. Start chooses the heating/cooling
coefficient from the comfort error, independently of `heatCoolMode`.

Stop eligibility requires enabled stop and active schedule. Valid space
temperature and a mode other than stop in process enter stop calculation.
Heating lead is `int((space-lower) * heating_drift_mpd)`; cooling lead is
`int((upper-space) * cooling_drift_mpd)`. Those assignments occur only when
space is **above the lower limit**. At/below that limit the previous lead is
retained (755–775). Cooling above the upper limit can produce negative lead.

The date gate compares day of year, not year or absolute event recency (720).
Both calculations first clamp to earliest start; stop then clamps to earliest
stop. A command fires strictly after calculated time **or** strictly after the
schedule event (781–808). That second alternative can bypass an earliest time
configured later than the event. No new late-command guard is added.

Start and stop commands carry both a Boolean and a null status. Start in process
produces a non-null true start; stop in process produces a non-null **false**
stop. Other commands are false/null (815–831). Opaque non-null status flags are
retained when the null bit changes. `space_temp_valid` is the caller/SDK
adapter's `BStatus.isValid()` result; input statuses other than current space
temperature are ignored by this class.

## Native learning

Four independent minutes-per-degree coefficients start at 10. Adjustment
requires dynamic adjustment enabled, unfinished analysis, and valid current
space status, then dispatches using the **last** mode (836–842). Correct
direction is mandatory. A sample completes at comfort crossing **or** a
schedule transition, even after an arbitrarily small positive temperature
change (849–889). There is no minimum movement/sample count, coefficient clamp,
epsilon, cooldown, finite-value filter, or outlier rejection.

The observed coefficient is integer elapsed minutes divided by directional
temperature change. Each corresponding coefficient becomes
`(old * m + observed) / (m + 1)`, with default `m=2`, hence event-weighted
alpha 1/3. This is not an EMA of degrees/minute. Partial schedule-transition
observations are not full time-to-comfort labels.

Float32 operations follow Java expression order. Start casts the temperature
difference once; stop casts both operands before subtracting. Java integer
narrowing, signed overflow and IEEE floating division are reproduced. Thus
zero/negative/nonfinite parameters and a stop difference rounded to zero are
not silently repaired.

`startDone` resets while start is disabled or during the first minute after
midnight (708–710). `analysisComplete` resets outside in-process modes (831).
Changing a user-defined coefficient while running and at steady state copies
that coefficient and records `parameterResetTime`; it does not reset either
latch (666–686). Initial zero user-defined properties are not automatically
copied over the active defaults.

## Explicit SDK compatibility layer

`TimeAdapter` uses an explicit station timezone, UTC by default. It emulates
`BAbsTime.NULL` as the Unix epoch, `delta(other)` as other minus self,
`getMinutes()` as signed truncation toward zero, millisecond precision, and
relative-to-clock time conversion modulo 24 hours. These are **stub conventions**,
not independently established Niagara SDK behavior. The Java differential
oracle uses the same conventions. Timezones, DST, NULL semantics, and
out-of-range SDK conversion need actual Niagara fixtures before certification.

An injected callable clock is read at each source clock-read location. Passing
`tick(..., now=...)` explicitly freezes those reads to one timestamp for replay.
`next_clock_ticket()` models a next-top-of-minute ticket plus 15 seconds and a
one-minute period (662–663). A five-minute adapter changes observation and
decision opportunities and is not claimed equivalent to native execution.

Native action handlers are empty (695–699). Events expose trigger and learning
records; an optional observer receives copies after the tick. This does not
emulate Niagara action queues, property callback interleavings, downstream
links, persistence, or equipment interlocks. `status_flags` are opaque retained
metadata, not a fabricated mapping of Niagara's status-bit definitions.
Human-readable messages use Python datetime/number formatting; Niagara's
localized `toString`/`DecimalFormat` rendering is outside the compared contract.

## Research boundary and verification

`OptimizedStartStop` has no alternate predictor or selector. The separately named
`ResearchOptimizedStartStop` accepts `lead_predictor(kind, inputs,
state_snapshot, default_lead)`. It calls the predictor only at the original
prediction branches and then uses native time clamps/control. It intentionally
changes native lead prediction; snapshots prevent the callback from editing
native state. A research controller may also replace coefficient supply, but
that likewise intentionally changes native end-to-end behavior. Model fitting
constraints, MAE histories and champion switching must not add hidden native
learning restrictions. Predictions must be recorded before the outcome and
training, and score labels must distinguish partial rates, completed target
durations, comfort error and censored observations.

Analytical Python fixtures cover the native branches and numeric boundaries.
The optional Java oracle mechanically extracts the control/analysis method
bodies from the owner-supplied file at test time, compiles generated wrappers
and classes under TEMP, and compares traces against Python. The repository does
not bundle the proprietary file or generated Java/binaries. Passing these tests
establishes agreement with extracted methods **under declared SDK stubs**, not
Niagara runtime equivalence or field safety.
