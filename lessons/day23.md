# Day 23 — The Big Equation: Multiple Regression

**Goal:** Present the full Model 3 formula and explain each coefficient.

## 1. Full Model

Model 3 uses two features:

* `x1 = DeltaT`
* `x2 = DeltaT * WF`

The prediction is:

```
t = a * x1 + b * x2 + d
```

where:
* `a` captures how ΔT alone affects time.
* `b` captures how the product of ΔT and weather influences time.
* `d` is an intercept term.

## 2. Interpretation

If `b` is large, outdoor conditions strongly affect warm‑up.  If `b` is near zero, Model 1 may suffice.

## 3. Key Takeaway

Model 3 blends indoor and outdoor effects through a linear combination of two features.
