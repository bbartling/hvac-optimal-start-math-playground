# Day 38 — The Technician’s Guess

**Goal:** Add a fixed buffer to Monday predictions

## 1. Concept and Definitions

Many technicians handle Mondays by simply adding a fixed number of
minutes (e.g., 60 min) to the predicted start time.  This crude
adjustment acknowledges the extra cold mass without changing the
underlying model.  While not mathematically elegant, it often works.
You can implement this by adding a constant to your computed t_opt on
Mondays.

## 2. How to Use It

Apply the concepts above using the formula or algorithm provided. Refer to the mini examples below for a demonstration.

## 3. Why This Matters

Understanding this concept allows you to build more accurate and efficient optimal‑start models, improving comfort and energy savings.

## 4. Mini‑Examples

Here's a simple Python demonstration:

```python
# Technician’s Monday adjustment
delta_t = 6.0
rate = 0.20
t_model = delta_t / rate
t_monday = t_model + 60  # add 60 minute buffer
print(f'Model prediction: {t_model:.1f} min')
print(f'Monday prediction with buffer: {t_monday:.1f} min')
```

## 5. Micro‑Exercises

1. Pick a buffer (e.g., 30 min) and see how well it matches Monday data.
2. Why might a fixed buffer be more robust than a ratio multiplier?
3. Describe a scenario where adding a constant buffer could cause overshoot.
4. Create a simple Python file that performs the calculations from this lesson.
   Use only basic variables, arithmetic, print statements and at most a `for` loop over a list. Avoid defining functions or using `zip`.
   Hint: replicate the structure of the examples above but use your own numbers or dataset.

## 6. Key Takeaway

A simple constant added to Monday run times often outperforms purely data‑driven models on the first day of the week.
