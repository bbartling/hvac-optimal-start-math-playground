# Day 28 — Week 4 Review: Is It Worth It?

**Goal:** Weigh the benefits of Model 3 against its complexity

## 1. Concept and Definitions

Model 3 is more accurate on average than Model 1 but requires more
computation, data and careful tuning.  In many cases the simpler
quadratic model performs nearly as well【913477360246089†L448-L476】.  Use
this review to decide when the extra effort of multiple regression is
justified.  Consider zone type, available sensors and technical
support.

## 2. How to Use It

Apply the concepts above using the formula or algorithm provided. Refer to the mini examples below for a demonstration.

## 3. Why This Matters

Understanding this concept allows you to build more accurate and efficient optimal‑start models, improving comfort and energy savings.

## 4. Mini‑Examples

Here's a simple Python demonstration:

```python
# Compare Model 1 and Model 3 predictions on a sample day
delta_t = 6.0
WF = 0.7
# Model 1 coefficients
a1, b1 = 1.2, 3.0
t1 = a1 * (delta_t ** 2) + b1
# Model 3 coefficients
a3, b3, d3 = 1.8, 1.2, 2.5
t3 = a3 * delta_t + b3 * (delta_t * WF) + d3
print(f'Model1: {t1:.1f} min, Model3: {t3:.1f} min')
```

## 5. Micro‑Exercises

1. For which ΔT values does Model 3 improve significantly over Model 1?
2. What additional sensors are required to implement Model 3?
3. How would you justify deploying Model 3 to a facilities manager?
4. Create a simple Python file that performs the calculations from this lesson.
   Use only basic variables, arithmetic, print statements and at most a `for` loop over a list. Avoid defining functions or using `zip`.
   Hint: replicate the structure of the examples above but use your own numbers or dataset.

## 6. Key Takeaway

Model 3 can offer marginal gains but at the cost of complexity.  Evaluate the trade‑offs before choosing a model.
