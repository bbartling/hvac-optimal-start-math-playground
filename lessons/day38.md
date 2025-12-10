# Day 38 — The Technician’s Guess

**Goal:** Add a fixed buffer to Monday predictions

Many technicians handle Mondays by simply adding a fixed number of
minutes (e.g., 60 min) to the predicted start time.  This crude
adjustment acknowledges the extra cold mass without changing the
underlying model.  While not mathematically elegant, it often works.
You can implement this by adding a constant to your computed t_opt on
Mondays.

## Python Mini‑Lesson

```python
# Technician’s Monday adjustment
delta_t = 6.0
rate = 0.20
t_model = delta_t / rate
t_monday = t_model + 60  # add 60 minute buffer
print(f'Model prediction: {t_model:.1f} min')
print(f'Monday prediction with buffer: {t_monday:.1f} min')
```

## Exercises

1. Pick a buffer (e.g., 30 min) and see how well it matches Monday data.
2. Why might a fixed buffer be more robust than a ratio multiplier?
3. Describe a scenario where adding a constant buffer could cause overshoot.

## Key Takeaway

A simple constant added to Monday run times often outperforms purely data‑driven models on the first day of the week.
