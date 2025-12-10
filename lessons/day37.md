# Day 37 — Why Math Fails Here

**Goal:** Explain the limitations of data‑driven models on Mondays

Data‑driven models rely on recent history to predict warm‑up.  Mondays
behave like a different system because the building has been unheated for
48 hours.  The thermal mass is colder and takes longer to warm.
Mathematically, the parameters learned from weekdays don’t apply.  This
lesson explores why the assumptions of self‑tuning models break down.

## Python Mini‑Lesson

```python
# Compare residuals on Monday vs other days
predicted_times = [30, 32, 31, 29]  # Tue–Fri predicted
actual_times = [31, 33, 32, 30]
week_error = [a - p for p, a in zip(predicted_times, actual_times)]
mon_pred = 30
mon_actual = 50
mon_error = mon_actual - mon_pred
print('Week errors:', week_error)
print('Monday error:', mon_error)
```

## Exercises

1. Look at your historical data.  How much larger are Monday errors than weekday errors?
2. Why can’t you simply include Monday data in the same training set?
3. Suggest reasons why the building cools more over a long weekend.

## Key Takeaway

Mondays violate the assumption that the system behaves consistently day‑to‑day.  Recognising this limitation guides you toward hybrid or rule‑based fixes.
