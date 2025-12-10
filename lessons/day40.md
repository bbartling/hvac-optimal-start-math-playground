# Day 40 — Experiment: Separate Histories

**Goal:** Maintain a distinct model just for Mondays

## 1. Concept and Definitions

Another approach is to treat Mondays as a separate class and train a
dedicated model using only Monday data.  This avoids contaminating the
weekday model with cold‑soaked data.  The downside is that you need
many weeks of data to populate the Monday history.

## 2. How to Use It

Apply the concepts above using the formula or algorithm provided. Refer to the mini examples below for a demonstration.

## 3. Why This Matters

Understanding this concept allows you to build more accurate and efficient optimal‑start models, improving comfort and energy savings.

## 4. Mini‑Examples

Here's a simple Python demonstration:

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

## 5. Micro‑Exercises

1. How many weeks of data would you need for a reliable Monday model?
2. What are the pros and cons of maintaining two separate models?
3. Could you use a one‑hot encoded feature for Monday instead of two models?
4. Create a simple Python file that performs the calculations from this lesson.
   Use only basic variables, arithmetic, print statements and at most a `for` loop over a list. Avoid defining functions or using `zip`.
   Hint: replicate the structure of the examples above but use your own numbers or dataset.

## 6. Key Takeaway

Separating Monday data allows each model to capture its own dynamics, but it requires more data and management.
