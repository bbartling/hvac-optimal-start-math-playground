# Day 17 — Solve Model 1 by Hand

**Goal:** Practise solving a quadratic warm‑up model from scratch using real datapoints.

Today you’ll go through the mechanics of computing Model 1 coefficients step by step, just as you would in a notebook or spreadsheet.

## 1.  Collect the Data

Suppose you observe three mornings:

| ΔT (°F) | t (min) |
|---------|---------|
| 4       | 22      |
| 6       | 38      |
| 8       | 62      |

Compute `x = (DeltaT)^2` for each:

| ΔT | x = (ΔT)² | t |
|----|-----------|---|
| 4  | 16        | 22 |
| 6  | 36        | 38 |
| 8  | 64        | 62 |

## 2.  Solve for a and b

Use any two rows (for example, the first two) to solve:

```
22 = a*16 + b
38 = a*36 + b
```

Subtract the first equation from the second:

```
16 = a*(36 − 16) → a = 16 / 20 = 0.8
```

Plug back to find b:

```
22 = 0.8*16 + b → b = 22 − 12.8 = 9.2
```

Your Model 1 equation becomes `t = 0.8*(DeltaT)^2 + 9.2`.

## 3.  Validate with the Third Point

Check ΔT = 8 °F (x = 64):

```
t_predicted = 0.8*64 + 9.2 = 51.2 + 9.2 = 60.4
```

The actual was 62 min, so the model is close.  If it were off by a lot, you could average the results from different pairs of points or use more sophisticated fitting.

## Mini‑Exercises

1. Use datapoints (ΔT = 3 °F, t = 14 min), (ΔT = 5 °F, t = 30 min) and (ΔT = 7 °F, t = 52 min).  Compute `a` and `b` from the first two points and verify with the third.
2. Try solving for `a` and `b` using the second and third points instead.  Do you get a slightly different result?  How would you combine them?

## Key Takeaway

Model 1 coefficients are solved just like a line — you set up two equations and subtract them.  Checking your model against a third datapoint helps validate your fit and suggests whether the building behaves consistently or is more complex.