# Day 33 — Comparing Log vs. Quadratic

**Goal:** Evaluate which model fits your building better

## 1. Concept and Definitions

Both Model 1 and Model 4 address non‑linear warm‑up, but they differ
mathematically.  The quadratic model grows with (ΔT)², while the
logarithmic model slows dramatically near set point.  Compare the
predictions of both models on the same dataset to see which aligns
better with measured times.

## 2. How to Use It

Apply the concepts above using the formula or algorithm provided. Refer to the mini examples below for a demonstration.

## 3. Why This Matters

Understanding this concept allows you to build more accurate and efficient optimal‑start models, improving comfort and energy savings.

## 4. Mini‑Examples

Here's a simple Python demonstration:

```python
# Compare Model 1 and Model 4 predictions
import math
delta_ts = [2, 5, 8]
alpha1_a, alpha1_b = 1.0, 3.0
decay_rate = 0.8
deadband = 0.5
for delta in delta_ts:
    t_quad = alpha1_a * (delta ** 2) + alpha1_b
    t_log = math.log(deadband / delta) / math.log(decay_rate)
    print(f'ΔT={delta}°F → Quadratic={t_quad:.1f} min, Logarithmic={t_log:.1f} min')
```

## 5. Micro‑Exercises

1. For your building, measure warm‑up times at multiple ΔT values and compare which model fits better.
2. Why might Model 4 under‑predict time for large ΔT?
3. Can you combine aspects of both models into a hybrid?
4. Create a simple Python file that performs the calculations from this lesson.
   Use only basic variables, arithmetic, print statements and at most a `for` loop over a list. Avoid defining functions or using `zip`.
   Hint: replicate the structure of the examples above but use your own numbers or dataset.

## 6. Key Takeaway

Different buildings may favour different non‑linear models.  Comparing predictions to real data reveals which model suits your situation.
