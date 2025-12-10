# Day 35 — Week 5 Review: The Full Arsenal

**Goal:** Reflect on the four models studied so far

At this point you have learned linear (Model 0), quadratic (Model 1),
ratio‑adjusted (Model 2) and logarithmic (Model 4) models.  Each model
adds complexity to capture a particular effect: smoothing, non‑linearity,
weather and slowing near set point.  Review their strengths and
weaknesses, and think about which models to deploy in your facility.

## Python Mini‑Lesson

```python
# Example summary table of model predictions for ΔT=6°F
delta_t = 6.0
rate = 0.25
t0 = delta_t / rate
alpha1_a, alpha1_b = 1.2, 4.0
t1 = alpha1_a * (delta_t ** 2) + alpha1_b
alpha2a = 6/30
t2_base = delta_t / alpha2a
ratio = (32 - 28) / (32 - 20)
t2 = t2_base * ratio
decay_rate = 0.8
deadband = 0.5
t4 = math.log(deadband / delta_t) / math.log(decay_rate)
print(f'Model0={t0:.1f}, Model1={t1:.1f}, Model2={t2:.1f}, Model4={t4:.1f}')
```

## Exercises

1. List one advantage and one disadvantage of each model.
2. Which model requires the most data and why?
3. In what situations might a simple model outperform a complex one?

## Key Takeaway

Each model captures different physical phenomena.  Selecting the right tool depends on your zone type, data availability and control goals.
