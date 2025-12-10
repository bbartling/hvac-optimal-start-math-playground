# Day 21 — Week 3 Review: Perimeter vs. Core

**Goal:** Decide when to use Model 2 versus Model 1

Model 1 assumes indoor conditions dominate and is best for interior or
high‑mass zones.  Model 2 adds a weather correction and is better for
perimeter zones exposed to outdoor fluctuations.  Review your own
buildings: where would each model work well?  Consider insulation,
window area and the sensitivity of the space to outdoor swings.

## Python Mini‑Lesson

```python
# Compare Model 1 and Model 2 predictions for the same zone
delta_t = 6.0
alpha1_a, alpha1_b = 1.0, 4.0
t_model1 = alpha1_a * (delta_t ** 2) + alpha1_b
# Model 2 base time using yesterday’s rate
alpha2a = 6.0 / 30.0  # yesterday ΔT=6°F, time=30 min
t_base = delta_t / alpha2a
ratio = (32 - 28) / (32 - 20)  # colder today
t_model2 = t_base * ratio
print(f'Model1 prediction: {t_model1:.1f} min')
print(f'Model2 prediction: {t_model2:.1f} min')
```

## Exercises

1. For an interior zone, which model is likely more accurate?  Why?
2. How does the presence of windows influence your choice of model?
3. Suggest additional data (e.g., solar gain) that might further improve predictions.

## Key Takeaway

Selecting the right model depends on the zone’s exposure and thermal mass.  There is no one‑size‑fits‑all solution.
