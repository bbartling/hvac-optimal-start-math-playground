# Day 33 — Comparing Log vs. Quadratic

**Goal:** Evaluate which model fits your building better

Both Model 1 and Model 4 address non‑linear warm‑up, but they differ
mathematically.  The quadratic model grows with (ΔT)², while the
logarithmic model slows dramatically near set point.  Compare the
predictions of both models on the same dataset to see which aligns
better with measured times.

## Python Mini‑Lesson

```python
# Compare Model 1 and Model 4 predictions
import math
delta_ts = [2, 5, 8]
alpha1_a, alpha1_b = 1.0, 3.0
decay_rate = 0.8
deadband = 0.5
for delta in delta_ts:
    t_quad = alpha1_a * (delta ** 2) + alpha1_b
    t_log = math.log(deadband / delta) / math.log(decay_rate)
    print(f'ΔT={delta}°F → Quadratic={t_quad:.1f} min, Logarithmic={t_log:.1f} min')
```

## Exercises

1. For your building, measure warm‑up times at multiple ΔT values and compare which model fits better.
2. Why might Model 4 under‑predict time for large ΔT?
3. Can you combine aspects of both models into a hybrid?

## Key Takeaway

Different buildings may favour different non‑linear models.  Comparing predictions to real data reveals which model suits your situation.
