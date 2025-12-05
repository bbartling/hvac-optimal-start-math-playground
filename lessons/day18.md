# Day 18 — PNNL Model 3 Structure

**Goal:** Learn how Model 3 incorporates weather into the warm‑up prediction and the variables involved.

Model 3 extends Model 1 by introducing a **weather factor (WF)** term.  It accounts for the fact that a 6 °F setback on a 50 °F day warms faster than the same setback when it’s 20 °F outside.

## 1.  Model Formula

```
t_predicted = a * (DeltaT) + b * (DeltaT * WF) + d
```

Where:

* `DeltaT` is the temperature difference to recover.
* `WF` is the **weather factor**.  PNNL defines it as `(OAT_ref − OAT) / (OAT_ref − OAT_min)`, where `OAT` is the current outdoor air temperature, `OAT_ref` is a mild reference (e.g. 65 °F) and `OAT_min` is a cold reference (e.g. 0 °F).  WF ranges from 0 (mild) to 1 (very cold).
* `a`, `b` and `d` are coefficients learned from data.

Notice there are now two inputs:

```
x1 = DeltaT
x2 = DeltaT * WF
```

## 2.  Solving for the Coefficients

You need at least three warm‑up mornings with different ΔT and WF combinations.  Each morning gives one equation of the form `t = a*x1 + b*x2 + d`.  Solve the resulting 3×3 system (see Day 4 for the process).  Blend the new coefficients into the existing ones with a smoothing factor α.

## 3.  When to Use Model 3

* If your building warms significantly slower on cold mornings compared with mild mornings at the same ΔT.
* If an outdoor air sensor is available to compute WF reliably.
* When Model 0 and Model 1 predictions consistently under‑ or over‑shoot depending on weather.

## Mini‑Exercises

1. Compute WF if `OAT = 30 °F`, `OAT_ref = 65 °F` and `OAT_min = 0 °F`.
2. For ΔT = 5 °F and your WF from (1), calculate `x1` and `x2`.
3. Write the general equation for `t_predicted` using unknown coefficients `a`, `b` and `d`.

## Key Takeaway

Model 3 augments the quadratic framework with a weather factor.  It recognises that large setbacks on cold mornings take even longer to warm up.  This makes predictions more accurate across seasons.