# Day 37 — Why Math Fails Here

**Goal:** Explain the limitations of data‑driven models on Mondays

## 1. Concept and Definitions

Data‑driven models rely on recent history to predict warm‑up.  Mondays
behave like a different system because the building has been unheated for
48 hours.  The thermal mass is colder and takes longer to warm.
Mathematically, the parameters learned from weekdays don’t apply.  This
lesson explores why the assumptions of self‑tuning models break down.

## 2. How to Use It

Apply the concepts above using the formula or algorithm provided. Refer to the mini examples below for a demonstration.

## 3. Why This Matters

Understanding this concept allows you to build more accurate and efficient optimal‑start models, improving comfort and energy savings.

## 4. Mini‑Examples

Here's a simple Python demonstration:

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

## 5. Micro‑Exercises

1. Look at your historical data.  How much larger are Monday errors than weekday errors?
2. Why can’t you simply include Monday data in the same training set?
3. Suggest reasons why the building cools more over a long weekend.
4. Create a simple Python file that performs the calculations from this lesson.
   Use only basic variables, arithmetic, print statements and at most a `for` loop over a list. Avoid defining functions or using `zip`.
   Hint: replicate the structure of the examples above but use your own numbers or dataset.

## 6. Key Takeaway

Mondays violate the assumption that the system behaves consistently day‑to‑day.  Recognising this limitation guides you toward hybrid or rule‑based fixes.
