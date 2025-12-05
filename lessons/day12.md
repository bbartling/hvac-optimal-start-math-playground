# Day 12 — Solving for a and b (Manual Math)

**Goal:** Derive the ordinary least squares formulas for estimating a and b from multiple points.

## 1. Ordinary Least Squares (OLS)

When you have more than two data points, the best‑fit line minimises the squared errors.  For Model 1, the formulas are:

```
a = (N * Σ(x*t) - Σx * Σt) / (N * Σ(x**2) - (Σx)**2)
b = (Σt - a * Σx) / N
```

where `N` is the number of data points, `x = DeltaT**2`, and `t` is the warm‑up time.

## 2. Example with Three Points

For (x, t) pairs: (4,10), (16,24), (36,44):

* Σx = 4 + 16 + 36 = 56
* Σt = 10 + 24 + 44 = 78
* Σ(x*t) = 4*10 + 16*24 + 36*44 = 40 + 384 + 1584 = 2008
* Σ(x**2) = 4**2 + 16**2 + 36**2 = 16 + 256 + 1296 = 1568
* N = 3

Compute `a` and `b` accordingly and verify.

## 3. Key Takeaway

OLS lets you use more data for better estimates.  The math looks messy but is straightforward to implement in Python.
