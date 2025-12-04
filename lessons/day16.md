# Day 16 — PNNL Model 1 (Quadratic Algebraic Tuning)

**Goal:** Understand the full structure of Model 1 and why squaring ΔT makes predictions safer on cold mornings.

Model 1 improves on Model 0 by allowing the minutes‑per‑degree to grow with ΔT.  It uses a quadratic form and solves for its coefficients using 2×2 systems.

## 1.  Model Formula

```
t_predicted = a * (DeltaT)^2 + b
```

Where `a` and `b` are learned from historical warm‑up data via algebraic regression.  `DeltaT` is the current temperature difference to close.

## 2.  Solving for a and b

Collect at least two warm‑up datapoints.  For each datapoint, compute `x = (DeltaT)^2` and `t` (minutes).  Solve the 2×2 system:

```
t1 = a*x1 + b
t2 = a*x2 + b
```

See Day 4 for details on solving small systems.  After solving, blend the new `a` and `b` into the existing coefficients using a smoothing factor α.

## 3.  Strengths and Limitations

* **Strengths:** Captures the slower warm‑up on large ΔT days; requires only two coefficients; easier to tune than Model 3.
* **Limitations:** Cannot account for weather or other external factors; still assumes behaviour is solely a function of ΔT.

## Mini‑Exercises

1. Given warm‑up datapoints (ΔT = 3 °F, t = 18 min) and (ΔT = 7 °F, t = 52 min), compute `a` and `b` using `x = (DeltaT)^2`.
2. Using your `a` and `b` from (1), predict the warm‑up time for ΔT = 5 °F.

## Key Takeaway

Model 1 is a simple quadratic curve fit to warm‑up data.  It adds curvature to handle large setbacks without resorting to complex statistics.  If your building warms slowly when it’s cold outside, Model 1 is a good next step beyond the linear model.