# Day 42 — Final Project: The Monday Showdown

**Goal:** Compare hybrid, technician and regression predictions on real data

## 1. Concept and Definitions

For a final challenge gather five real Monday warm‑up cases.  For each
case compute the prediction from Model 3, the technician’s guess (+60
min) and the hybrid controller from Day 41.  Compare them to the
actual runtime and decide which method performs best.  This exercise
solidifies your understanding of the Monday problem.

## 2. How to Use It

Apply the concepts above using the formula or algorithm provided. Refer to the mini examples below for a demonstration.

## 3. Why This Matters

Understanding this concept allows you to build more accurate and efficient optimal‑start models, improving comfort and energy savings.

## 4. Mini‑Examples

Here's a simple Python demonstration:

```python
# Placeholder code for the Monday showdown (fill in with your data)
cases = [
    {'delta_t': 7, 'actual': 95},
    {'delta_t': 5, 'actual': 70},
    {'delta_t': 6, 'actual': 80},
    {'delta_t': 4, 'actual': 65},
    {'delta_t': 8, 'actual': 100},
]
WF = 0.6
a3, b3, d3 = 1.7, 1.2, 3.5
for case in cases:
    delta_t = case['delta_t']
    m3 = a3 * delta_t + b3 * (delta_t * WF) + d3
    tech = delta_t / 0.22 + 60
    hybrid = m3 + 45
    print("DeltaT={}F -> actual={} min, Model3={:.1f}, Tech={:.1f}, Hybrid={:.1f}".format(delta_t, case['actual'], m3, tech, hybrid))
```

## 5. Micro‑Exercises

1. Replace the placeholder data with your own Monday cases and record the results.
2. Which method had the smallest error on average?
3. How could you further improve predictions for extremely cold Mondays?
4. Create a simple Python file that performs the calculations from this lesson.
   Use only basic variables, arithmetic, print statements and at most a `for` loop over a list. Avoid defining functions or using `zip`.
   Hint: replicate the structure of the examples above but use your own numbers or dataset.

## 6. Key Takeaway

Comparing predictions across methods on real data highlights the strengths and weaknesses of each approach and prepares you for real‑world deployment.
