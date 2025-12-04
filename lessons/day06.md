# Day 6 — What “Self‑Tuning” Really Means

**Goal:** Understand how the models learn from new data and adapt themselves over time.

Buildings and weather aren’t static.  A fixed warm‑up model will be wrong within weeks.  Self‑tuning means the model updates its coefficients automatically as new mornings are observed.  There are two mechanisms in optimal start.

## 1.  Why HVAC Models Must Self‑Tune

The building envelope, equipment performance, occupancy and weather all change.  Night setbacks may be deeper on some days, coils get fouled, economisers behave differently.  A self‑tuning model stays on top of these shifts by recalibrating itself each morning.

## 2.  Two Flavours of Self‑Tuning

### 2.1 Self‑tuning with EMA (Model 0)

Model 0 uses an **exponential moving average** to learn a single slope — the degrees‑per‑minute rate.  After each warm‑up run, you compute the observed rate and blend it into the previous rate:

```
newRate = oldRate + alpha * (observedRate − oldRate)
```

where `observedRate = DeltaT / actualMinutes` and `alpha` (0–1) determines how quickly the model adapts.  Niagara stores this in the `degreesPerMinute` slot.

### 2.2 Self‑tuning via Regression (Models 1 & 3)

Models 1 and 3 have multiple coefficients.  Each morning’s datapoint provides a new equation.  You solve for `a`, `b` (and `d` for Model 3) and then blend the new values into the old ones:

```
a_new = (1 − alpha) * a_old + alpha * a_today
b_new = (1 − alpha) * b_old + alpha * b_today
d_new = (1 − alpha) * d_old + alpha * d_today  (Model 3)
```

This smoothing keeps the model stable even when a single morning is unusual (e.g. a holiday).

## 3.  Self‑Tuning Example — EMA (Model 0)

* Yesterday’s rate: 0.20 °F/min
* Today’s warm‑up: ΔT = 6 °F in 40 min → observedRate = 6/40 = 0.15 °F/min
* `alpha = 0.1`

```
newRate = 0.20 + 0.1 * (0.15 − 0.20) = 0.20 − 0.005 = 0.195 °F/min
```

The model nudges its rate downward because the building was slower today.

## 4.  Self‑Tuning Example — Model 1 Regression

Suppose your current Model 1 coefficients are `a_old = 0.8`, `b_old = 10`.  Today’s warm‑up is ΔT = 6 °F (x = 36), t = 38 min.  You estimate a temporary slope:

```
a_today = t / x = 38 / 36 ≈ 1.0556
```

Then blend with a small `alpha = 0.1`:

```
a_new = 0.9 * 0.8 + 0.1 * 1.0556 ≈ 0.8256
b_new = 10  (unchanged for a single‑point update)
```

The slope grows slightly because today’s warm‑up was slower per degree.

## 5.  Day 6 Micro‑Exercise

*Old rate* = 0.18 °F/min, *observed rate* = 0.24 °F/min, `alpha = 0.15`:

1. Compute the new rate using the EMA formula.

For Models 1 and 3:

*Old `a`* = 1.1, *old `b`* = 8.0.  Today’s solved values: `a_today` = 1.5, `b_today` = 6.0, `alpha` = 0.10.

2. Compute `a_new` and `b_new`.

## 6.  Key Takeaway From Day 6

Self‑tuning is not magic.  It’s just a weighted average of yesterday’s coefficients and today’s observations.  Model 0 uses an EMA on degrees‑per‑minute.  Models 1 and 3 use smoothed algebraic regression.  Choosing a reasonable `alpha` ensures the model adapts without becoming jumpy.