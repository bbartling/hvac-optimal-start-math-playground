# Day 3 — Quadratics Refresher: Why Model 1 Uses `(ΔT)²`

**Goal:** See why a simple line isn’t enough and how a quadratic model bends to match real building behaviour.

In cold climates or buildings with heavy envelopes, warm‑up time does **not** increase linearly as ΔT gets larger.  Model 1 introduces a quadratic term to capture this curvature.

## 1.  Why Quadratics Show Up in HVAC Warm‑Up

When ΔT is small (2–4 °F), the building warms almost linearly.  But as ΔT grows (8–12 °F), every extra degree tends to take more minutes than the one before:

* Coil capacity is fixed and may be maxed out.
* Heat transfer slows as the zone temperature approaches discharge air temperature.
* Envelope losses increase with larger ΔT.

A quadratic model allows the slope to increase with ΔT:

```
t = a * (DeltaT)^2 + b
```

Here `a` controls how quickly minutes per degree grow and `b` remains the baseline overhead.  This is exactly PNNL’s Model 1 structure.

## 2.  Visualising the Shape

Consider a model with `a = 0.5` and `b = 4` minutes:

| ΔT (°F) | x = (ΔT)² | Predicted time t (min) |
|---------|----------|------------------------|
| 2       | 4        | `0.5*4 + 4 = 6.0`    |
| 4       | 16       | `0.5*16 + 4 = 12.0`   |
| 8       | 64       | `0.5*64 + 4 = 36.0`   |

See how doubling ΔT from 4 °F to 8 °F **more than doubles** the predicted time (12 min → 36 min)?  That’s the curvature we need for accurate cold‑morning predictions.

## 3.  Solve a Quadratic Model by Hand

Suppose you observe three warm‑up events:

| ΔT (°F) | x = (ΔT)² | t (min) |
|---------|-----------|---------|
| 2       | 4         | 10      |
| 4       | 16        | 20      |
| 6       | 36        | 38      |

You assume the form `t = a*x + b`.  Pick two rows to solve for `a` and `b`.  Using (4 °F, 20 min) and (6 °F, 38 min):

```
a = (38 − 20) / (36 − 16) = 18 / 20 = 0.9
b = 20 − 0.9 * 16 = 20 − 14.4 = 5.6
```

So your quadratic warm‑up model is:

```
t = 0.9 * (DeltaT)^2 + 5.6
```

Check the third point (2 °F, 10 min) for validity (it should be close).

## 4.  Day 3 Micro‑Exercise

Try this simple exercise:

1. Compute `x = (DeltaT)^2` for ΔT = 3 °F, 5 °F, and 7 °F.
2. Using the model `t = 0.7 * x + 6`, predict warm‑up time for each x value.
3. Think practically: Does your building warm up linearly or quadratically for large ΔT?  (No wrong answer — just consider your experience.)

## 5.  Key Takeaway From Day 3

Quadratic models capture the reality that warm‑ups slow down as ΔT grows.  They’re solved using exactly the same algebra as a line, but with `x = (DeltaT)^2`.  PNNL’s Model 1 is simply this quadratic form with coefficients learned from field data.