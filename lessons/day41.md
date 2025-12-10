# Day 41 — Designing the Ultimate Hybrid

**Goal:** Combine models and rules for robust performance

A practical controller may use a hybrid strategy: if ΔT is small use
Model 0 (linear), if ΔT is moderate use Model 3 (regression), and if
Monday apply a buffer or multiplier on top of Model 3【913477360246089†L40-L46】.
This rule‑based logic captures the strengths of each approach.  You can
encode the logic as simple IF statements.

## Python Mini‑Lesson

```python
# Hybrid controller example
def hybrid_prediction(delta_t, is_monday=False):
    if delta_t < 2.0:  # small ΔT
        rate = 0.22
        return delta_t / rate
    # moderate to large ΔT: use Model 3
    WF = 0.6
    a3, b3, d3 = 1.5, 1.0, 3.0
    t_pred = a3 * delta_t + b3 * (delta_t * WF) + d3
    if is_monday:
        t_pred += 45  # technician buffer
    return t_pred
print(hybrid_prediction(1.5))
print(hybrid_prediction(6.0))
print(hybrid_prediction(6.0, is_monday=True))
```

## Exercises

1. Modify the hybrid logic to use a multiplier instead of an adder on Monday.
2. What criteria would you use to switch between Model 0 and Model 3?
3. How could you test the hybrid approach before deploying it live?

## Key Takeaway

Hybrid strategies blend simple models with conditional logic to handle special cases like Mondays.  They often outperform any single model.
