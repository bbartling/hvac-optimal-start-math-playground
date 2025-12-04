# Day 7 — Reading Warm‑Up Data Like a Model (Week 1 Review)

**Goal:** Learn to look at a small dataset and see what the model would learn.  This is your Week 1 capstone.

By now you understand ΔT, slopes, quadratics, systems and self‑tuning.  Day 7 teaches you to *interpret* real warm‑up logs and decide which model fits best.

## 1.  A Tiny Fake Building Dataset

Imagine you log five winter mornings:

| Day | Start Temp (°F) | Setpoint (°F) | ΔT | Warm‑Up Time (min) |
|----:|----------------:|--------------:|---:|-------------------:|
| 1   | 68              | 72            | 4  | 24                |
| 2   | 66              | 72            | 6  | 33                |
| 3   | 64              | 72            | 8  | 50                |
| 4   | 70              | 72            | 2  | 15                |
| 5   | 62              | 72            | 10 | 72                |

## 2.  Compute Time per Degree

For each day, divide minutes by ΔT to see the approximate minutes‑per‑degree:

```
Day 1: 24 / 4  ≈ 6.0
Day 2: 33 / 6  ≈ 5.5
Day 3: 50 / 8  ≈ 6.25
Day 4: 15 / 2  = 7.5
Day 5: 72 / 10 = 7.2
```

They are similar but not identical.  For very small ΔT the minutes‑per‑degree are higher, and for large ΔT they creep upward again.  This suggests a slight curvature, meaning a quadratic may fit better than a pure line.

## 3.  Decide: Linear or Quadratic?

* A **linear** model (`t = a*DeltaT + b`) assumes minutes‑per‑degree is roughly constant.  It may under‑predict on very cold days.
* A **quadratic** model (`t = a*(DeltaT)^2 + b`) lets the minutes‑per‑degree increase with ΔT.  It tends to over‑predict slightly on mild mornings but stays safe on cold ones.

Looking at the table, Day 3 and Day 5 take disproportionately longer than Day 2.  That hints that Model 1 might be more appropriate than Model 0 for this building.

## 4.  Mini‑Exercise — Interpret Your Own Data

Use this shorter set:

| Label | ΔT | Time (min) |
|------:|---:|-----------:|
| A     | 3  | 18        |
| B     | 5  | 26        |
| C     | 8  | 60        |

1. Compute `t / ΔT` for A, B and C.  Are the ratios roughly the same or do they drift up?
2. Based on your answer in (1), would you choose a linear model or a quadratic for this site?
3. Briefly explain why.

## 5.  Key Takeaway From Day 7

Reading a table of warm‑up data is the first step toward choosing and tuning the right model.  Look at the ratio of minutes to ΔT and see if it stays constant or increases.  If the ratio grows with ΔT or the weather has a big effect, you need a curvier model (Model 1 or Model 3).  This observational skill will help you set up and troubleshoot optimal start in the field.