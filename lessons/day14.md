# Day 14 — Week 2 Review: Model 0 vs. Model 1

**Goal:** Compare linear and quadratic predictions for typical scenarios

Model 0 predicts time as t = ΔT / rate; Model 1 uses t = α₁,a·(ΔT)² + α₁,b.
For small temperature differences the two models often agree, but for
large ΔT the quadratic term dominates.  Use this review to compare
predictions on the same dataset and decide which model is more
appropriate.

## Python Mini‑Lesson

```python
# Compare Model 0 and Model 1 predictions
delta_ts = [2, 5, 8]
rate = 0.20
alpha_a, alpha_b = 1.2, 3.0
for delta in delta_ts:
    t0 = delta / rate
    t1 = alpha_a * (delta ** 2) + alpha_b
    print(f'ΔT={delta}°F → Model0={t0:.1f} min, Model1={t1:.1f} min')
```

## Exercises

1. At what ΔT do the two models begin to diverge significantly?
2. Which model would you trust for an interior zone with small setbacks?
3. Suggest a hybrid approach for zones that occasionally experience large ΔT.

## Key Takeaway

Linear and quadratic models can both be useful.  The best choice depends on the magnitude of ΔT and the thermal characteristics of the zone.
