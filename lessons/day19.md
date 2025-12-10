# Day 19 — The Double Prediction

**Goal:** Combine the base time and weather ratio into the final runtime

Model 2 performs two steps: (1) predict a base time using yesterday’s
indoor rate, and (2) multiply by the weather ratio to account for
outdoor differences.  The final optimal start time is t_opt = t_base ×
ratio.  This structure keeps the indoor and outdoor effects separate and
makes the logic easy to implement in a BAS.

## Python Mini‑Lesson

```python
# Full Model 2 prediction
delta_t_y, time_y = 8.0, 40.0
alpha_2a = delta_t_y / time_y
delta_t_today = 6.0
t_base = delta_t_today / alpha_2a
T_ref = 32.0
oat_prev, oat_curr = 20.0, 10.0
ratio = (T_ref - oat_prev) / (T_ref - oat_curr)
t_opt = t_base * ratio
print(f'Base time={t_base:.1f} min, Ratio={ratio:.2f}, Final={t_opt:.1f} min')
```

## Exercises

1. Use your own ΔT and outdoor temperatures to compute Model 2’s t_opt.
2. Explain why the two‑step calculation is easier to tune than a single combined formula.
3. Under what conditions does Model 2 reduce to Model 0?

## Key Takeaway

Separating the indoor rate from the weather correction makes Model 2 intuitive and modular.  It also highlights when outdoor conditions significantly affect runtime.
