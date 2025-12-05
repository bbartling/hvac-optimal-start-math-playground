# Day 19 — Solve Model 3 Coefficients by Hand

**Goal:** Work through a practical example of solving the 3×3 system for Model 3’s coefficients.

Solving Model 3 is more involved than Model 1 because you have three unknowns (`a`, `b`, `d`).  You need three warm‑up datapoints with different ΔT and WF values.

## 1.  Example Data

Suppose you have these mornings:

| Morning | ΔT (°F) | WF   | Time (min) |
|--------:|--------:|-----:|-----------:|
| 1       | 4       | 0.2  | 20        |
| 2       | 6       | 0.5  | 45        |
| 3       | 8       | 0.8  | 80        |

Compute `x1` and `x2` for each:

| Morning | x1 (ΔT) | x2 (ΔT·WF) | t |
|--------:|--------:|-----------:|---:|
| 1       | 4       | 0.8        | 20 |
| 2       | 6       | 3.0        | 45 |
| 3       | 8       | 6.4        | 80 |

The system is:

```
20 = 4*a + 0.8*b + d
45 = 6*a + 3.0*b + d
80 = 8*a + 6.4*b + d
```

## 2.  Solve the System

Subtract the first equation from the second and third to eliminate `d`:

```
Eq2 − Eq1: 25 = (6 − 4)*a + (3.0 − 0.8)*b → 25 = 2*a + 2.2*b
Eq3 − Eq1: 60 = (8 − 4)*a + (6.4 − 0.8)*b → 60 = 4*a + 5.6*b
```

Now solve this 2×2 system:

```
25 = 2*a + 2.2*b
60 = 4*a + 5.6*b
```

Multiply the first equation by 2 and subtract:

```
50 = 4*a + 4.4*b
60 = 4*a + 5.6*b
→ 10 = 1.2*b → b = 10 / 1.2 ≈ 8.333
```

Plug `b` back into `25 = 2*a + 2.2*b`:

```
25 = 2*a + 2.2*8.333 ≈ 2*a + 18.333
→ a ≈ (25 − 18.333) / 2 = 3.333
```

Finally, find `d` using Eq1:

```
20 = 4*3.333 + 0.8*8.333 + d
20 = 13.333 + 6.667 + d
→ d = 20 − 20 = 0
```

So the estimated Model 3 is `t = 3.333*DeltaT + 8.333*(DeltaT*WF) + 0`.

## 3.  Blend Coefficients

As with Model 1, blend these new coefficients into the existing ones using a smoothing factor α to avoid overreacting to a single day.

## Mini‑Exercises

1. Replace the times in the example with 22, 48 and 85 minutes and solve again.  How do the coefficients change?
2. If `d` comes out negative, what might that indicate about your data?

## Key Takeaway

Solving Model 3 requires a bit more algebra but follows the same pattern: eliminate one variable at a time until you reduce the system to a solvable 2×2.  Once you have `a`, `b` and `d`, blend them into the model with a smoothing factor.