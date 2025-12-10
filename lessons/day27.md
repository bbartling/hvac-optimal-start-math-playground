# Day 27 — Tuning Model 3

**Goal:** Select history length and prevent overfitting

## 1. Concept and Definitions

Model 3 requires enough data to reliably estimate three parameters. 
Using too little history can overfit noise; using too much may make the
model slow to adapt.  PNNL recommends using around ten days of data
for coefficient updates.  You can also apply an EMA to the coefficients
similar to Model 1 to gradually adjust α₃,a, α₃,b and α₃,d.

## 2. How to Use It

Apply the concepts above using the formula or algorithm provided. Refer to the mini examples below for a demonstration.

## 3. Why This Matters

Understanding this concept allows you to build more accurate and efficient optimal‑start models, improving comfort and energy savings.

## 4. Mini‑Examples

Here's a simple Python demonstration:

```python
# Simple coefficient update with EMA
alpha = 0.1
coeff_old = {'a': 1.5, 'b': 0.8, 'd': 2.0}
coeff_new = {'a': 1.6, 'b': 1.0, 'd': 1.8}
for key in coeff_old:
    coeff_old[key] = coeff_old[key] + alpha * (coeff_new[key] - coeff_old[key])
print('Updated coefficients:', coeff_old)
```

## 5. Micro‑Exercises

1. What happens if you update coefficients after every single day versus every 10 days?
2. Suggest a method to detect overfitting in Model 3.
3. Could you assign different α values to α₃,a, α₃,b and α₃,d?  Why or why not?
4. Create a simple Python file that performs the calculations from this lesson.
   Use only basic variables, arithmetic, print statements and at most a `for` loop over a list. Avoid defining functions or using `zip`.
   Hint: replicate the structure of the examples above but use your own numbers or dataset.

## 6. Key Takeaway

Balancing the amount of history and the speed of adaptation prevents overfitting and keeps Model 3 responsive to real trends.
