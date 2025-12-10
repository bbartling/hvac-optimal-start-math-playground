# Day 44 — The Cost Function (MSE)

**Goal:** Quantify error using mean squared error

## 1. Concept and Definitions

Gradient descent minimises a cost function.  For regression the most
common choice is mean squared error (MSE), defined as the average of
(predicted − actual)² over all samples.  Squaring emphasises large
errors【485764260655805†L145-L161】.  The goal of training is to adjust the
weights so that MSE approaches zero.

## 2. How to Use It

Apply the concepts above using the formula or algorithm provided. Refer to the mini examples below for a demonstration.

## 3. Why This Matters

Understanding this concept allows you to build more accurate and efficient optimal‑start models, improving comfort and energy savings.

## 4. Mini‑Examples

Here's a simple Python demonstration:

```python
# Compute MSE for a set of predictions
pred = [30, 35, 28]
actual = [32, 34, 30]
errors = [(p - a) ** 2 for p, a in zip(pred, actual)]
mse = sum(errors) / len(errors)
print(f'MSE = {mse:.2f}')
```

## 5. Micro‑Exercises

1. Create your own predicted and actual lists and compute MSE.
2. Why do we square the errors instead of taking absolute values?
3. What would be the effect of using mean absolute error instead?
4. Create a simple Python file that performs the calculations from this lesson.
   Use only basic variables, arithmetic, print statements and at most a `for` loop over a list. Avoid defining functions or using `zip`.
   Hint: replicate the structure of the examples above but use your own numbers or dataset.

## 6. Key Takeaway

The mean squared error provides a single number that summarises prediction accuracy.  Minimising this cost drives the gradient descent algorithm.
