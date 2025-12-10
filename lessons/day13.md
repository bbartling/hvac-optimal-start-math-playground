# Day 13 — Self‑Tuning Model 1

**Goal:** Combine regression and EMA to adapt coefficients over time

## 1. Concept and Definitions

Instead of recomputing α₁,a and α₁,b from scratch each day, you can
apply an EMA to these coefficients, blending yesterday’s estimate with
today’s regression result.  This yields a slowly drifting quadratic model
that adapts to seasonal changes without overreacting to outliers.
The update rule is analogous to the rate EMA from Day 4:

    new_coeff = old_coeff + α × (observed_coeff − old_coeff)

where observed_coeff is the coefficient computed from the latest day’s
data.  Use small α values (e.g., 0.1) to obtain gradual tuning.

## 2. How to Use It

Apply the concepts above using the formula or algorithm provided. Refer to the mini examples below for a demonstration.

## 3. Why This Matters

Understanding this concept allows you to build more accurate and efficient optimal‑start models, improving comfort and energy savings.

## 4. Mini‑Examples

Here's a simple Python demonstration:

```python
# Self‑tuning quadratic coefficients
alpha = 0.1
# initial estimates
a_est, b_est = 1.0, 4.0
# new regression estimates from today
a_new, b_new = 1.4, 3.5
# update using EMA
a_est = a_est + alpha * (a_new - a_est)
b_est = b_est + alpha * (b_new - b_est)
print(f'Updated α₁,a={a_est:.2f}, α₁,b={b_est:.2f}')
```

## 5. Micro‑Exercises

1. Simulate 5 days of α₁,a estimates and apply α=0.2 to see how the coefficient evolves.
2. Why might you tune α differently for α₁,a and α₁,b?
3. Discuss the trade‑offs between fitting a fresh regression each day and using an EMA.
4. Create a simple Python file that performs the calculations from this lesson.
   Use only basic variables, arithmetic, print statements and at most a `for` loop over a list. Avoid defining functions or using `zip`.
   Hint: replicate the structure of the examples above but use your own numbers or dataset.

## 6. Key Takeaway

Applying an EMA to regression coefficients yields a model that gradually adapts to new data, blending stability with responsiveness.
