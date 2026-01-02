# Day B7 — Model 3 End‑to‑End

**Goal:** Build Model 3 regression from scratch with no libraries.

## 1. Concept and Definitions

Model 3 form:

    t = d + a·ΔT + b·(ΔT·WF)

## 2. How to Use It

Steps:
1. Build X and y
2. Compute XᵀX and Xᵀy
3. Solve for β
4. Predict runtime

## 3. Why This Matters

This implementation works in any language and any environment.

## 4. Mini‑Example

```python
beta = [d, a, b]
t = beta[0] + beta[1]*dT + beta[2]*(dT*WF)
```

## 5. Micro‑Exercises

1. Predict a new day’s runtime.
2. Compare against quadratic Model 1.
3. Add EMA smoothing to coefficients.
4. Port this logic to another language.

## 6. Key Takeaway

You now fully understand Model 3 — no libraries required.
