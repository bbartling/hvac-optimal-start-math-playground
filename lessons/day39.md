# Day 39 — Experiment: The Weekend Factor

**Goal:** Multiply Monday predictions by a factor

An alternative to a fixed buffer is to multiply the predicted time by a
factor (e.g., 1.2 or 1.3) on Mondays.  This scales the prediction
proportionally to the base time.  It can adapt better to different ΔT
values while still compensating for the cold soak.

## Python Mini‑Lesson

```python
# Apply a weekend multiplier
delta_t = 5.0
rate = 0.22
t_model = delta_t / rate
multiplier = 1.3
t_monday = t_model * multiplier
print(f'Base prediction: {t_model:.1f} min')
print(f'Multiplied for Monday: {t_monday:.1f} min')
```

## Exercises

1. Try multipliers of 1.1, 1.2 and 1.5.  Which best matches your Monday data?
2. What happens if ΔT is very small?  Does the multiplier still make sense?
3. How would you determine the ideal multiplier automatically?

## Key Takeaway

Multiplicative factors scale the runtime relative to the base prediction, adapting to the magnitude of ΔT better than a fixed buffer.
