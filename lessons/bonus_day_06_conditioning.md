# Day B6 — Conditioning & Stability

**Goal:** Learn why regression can become numerically unstable.

## 1. Concept and Definitions

If features are correlated or very large, XᵀX becomes ill‑conditioned.

Small noise → large coefficient swings.

## 2. How to Use It

Stability techniques:
- scale inputs
- add ridge term λI

## 3. Why This Matters

Real HVAC data is noisy and imperfect.

## 4. Mini‑Example

```python
lambda_ = 0.01
XTX[0][0] += lambda_
XTX[1][1] += lambda_
XTX[2][2] += lambda_
```

## 5. Micro‑Exercises

1. Scale ΔT values and refit Model 3.
2. Compare λ = 0 vs λ = 0.1.
3. Explain ridge regression in plain English.
4. Add ridge logic to your solver.

## 6. Key Takeaway

Stability matters more than perfect math.
