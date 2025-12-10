# Day 44 — The Cost Function (MSE)

**Goal:** Quantify error using mean squared error

Gradient descent minimises a cost function.  For regression the most
common choice is mean squared error (MSE), defined as the average of
(predicted − actual)² over all samples.  Squaring emphasises large
errors【485764260655805†L145-L161】.  The goal of training is to adjust the
weights so that MSE approaches zero.

## Python Mini‑Lesson

```python
# Compute MSE for a set of predictions
pred = [30, 35, 28]
actual = [32, 34, 30]
errors = [(p - a) ** 2 for p, a in zip(pred, actual)]
mse = sum(errors) / len(errors)
print(f'MSE = {mse:.2f}')
```

## Exercises

1. Create your own predicted and actual lists and compute MSE.
2. Why do we square the errors instead of taking absolute values?
3. What would be the effect of using mean absolute error instead?

## Key Takeaway

The mean squared error provides a single number that summarises prediction accuracy.  Minimising this cost drives the gradient descent algorithm.
