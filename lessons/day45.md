# Day 45 — The Gradient (The Nudge)

**Goal:** Compute gradients to update weights

The gradient of the cost function tells us how to adjust each weight to
reduce error.  For a simple linear model y = w·x, the gradient of the
MSE with respect to w is proportional to Σ (prediction − actual) × x.
We then update w ← w − η × gradient, where η is the learning rate【485764260655805†L152-L160】.

## Python Mini‑Lesson

```python
# Perform one gradient descent step for a single weight
x_data = [1, 2, 3]
y_actual = [2, 4, 6]
w = 0.0  # initial weight
learning_rate = 0.1
# Compute gradient of MSE w.r.t w
grad = sum((w * x - y) * x for x, y in zip(x_data, y_actual)) * 2 / len(x_data)
w = w - learning_rate * grad
print(f'Updated weight w={w:.2f}')
```

## Exercises

1. Repeat the update step 10 times and observe how w approaches the true value.
2. What happens if the learning rate η is too large?
3. Derive the gradient formula for a model with two weights.

## Key Takeaway

Gradients point in the direction of steepest error increase.  Updating weights opposite to the gradient reduces error over time.
