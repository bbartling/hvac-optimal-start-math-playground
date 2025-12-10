# Day 40 — Experiment: Separate Histories

**Goal:** Maintain a distinct model just for Mondays

Another approach is to treat Mondays as a separate class and train a
dedicated model using only Monday data.  This avoids contaminating the
weekday model with cold‑soaked data.  The downside is that you need
many weeks of data to populate the Monday history.

## Python Mini‑Lesson

```python
# Maintain separate EMA rates for weekdays and Mondays
alpha = 0.2
weekday_rate, monday_rate = 0.20, 0.15
# new observations
obs_weekday, obs_monday = 0.22, 0.13
weekday_rate = weekday_rate + alpha * (obs_weekday - weekday_rate)
monday_rate = monday_rate + alpha * (obs_monday - monday_rate)
print(f'Updated weekday rate = {weekday_rate:.3f}')
print(f'Updated Monday rate  = {monday_rate:.3f}')
```

## Exercises

1. How many weeks of data would you need for a reliable Monday model?
2. What are the pros and cons of maintaining two separate models?
3. Could you use a one‑hot encoded feature for Monday instead of two models?

## Key Takeaway

Separating Monday data allows each model to capture its own dynamics, but it requires more data and management.
