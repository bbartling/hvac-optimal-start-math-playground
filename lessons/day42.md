# Day 42 — Final Project: The Monday Showdown

**Goal:** Compare hybrid, technician and regression predictions on real data

For a final challenge gather five real Monday warm‑up cases.  For each
case compute the prediction from Model 3, the technician’s guess (+60
min) and the hybrid controller from Day 41.  Compare them to the
actual runtime and decide which method performs best.  This exercise
solidifies your understanding of the Monday problem.

## Python Mini‑Lesson

```python
# Placeholder code for the Monday showdown (fill in with your data)
cases = [
    {'delta_t': 7, 'actual': 95},
    {'delta_t': 5, 'actual': 70},
    {'delta_t': 6, 'actual': 80},
    {'delta_t': 4, 'actual': 65},
    {'delta_t': 8, 'actual': 100},
]
def model3_pred(delta_t):
    WF = 0.6
    a3, b3, d3 = 1.7, 1.2, 3.5
    return a3 * delta_t + b3 * (delta_t * WF) + d3
for case in cases:
    m3 = model3_pred(case['delta_t'])
    tech = case['delta_t'] / 0.22 + 60
    hybrid = model3_pred(case['delta_t']) + 45
    print("DeltaT={}F -> actual={} min, Model3={:.1f}, Tech={:.1f}, Hybrid={:.1f}".format(case['delta_t'], case['actual'], m3, tech, hybrid))
```

## Exercises

1. Replace the placeholder data with your own Monday cases and record the results.
2. Which method had the smallest error on average?
3. How could you further improve predictions for extremely cold Mondays?

## Key Takeaway

Comparing predictions across methods on real data highlights the strengths and weaknesses of each approach and prepares you for real‑world deployment.
