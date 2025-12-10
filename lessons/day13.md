# Day 13 — Self‑Tuning Model 1

**Goal:** Combine regression and EMA to adapt coefficients over time

Instead of recomputing α₁,a and α₁,b from scratch each day, you can
apply an EMA to these coefficients, blending yesterday’s estimate with
today’s regression result.  This yields a slowly drifting quadratic model
that adapts to seasonal changes without overreacting to outliers.
The update rule is analogous to the rate EMA from Day 4:

    new_coeff = old_coeff + α × (observed_coeff − old_coeff)

where observed_coeff is the coefficient computed from the latest day’s
data.  Use small α values (e.g., 0.1) to obtain gradual tuning.

## Python Mini‑Lesson

```python
# Self‑tuning quadratic coefficients
alpha = 0.1
# initial estimates
a_est, b_est = 1.0, 4.0
# new regression estimates from today
a_new, b_new = 1.4, 3.5
# update using EMA
a_est = a_est + alpha * (a_new - a_est)
b_est = b_est + alpha * (b_new - b_est)
print(f'Updated α₁,a={a_est:.2f}, α₁,b={b_est:.2f}')
```

## Exercises

1. Simulate 5 days of α₁,a estimates and apply α=0.2 to see how the coefficient evolves.
2. Why might you tune α differently for α₁,a and α₁,b?
3. Discuss the trade‑offs between fitting a fresh regression each day and using an EMA.

## Key Takeaway

Applying an EMA to regression coefficients yields a model that gradually adapts to new data, blending stability with responsiveness.
