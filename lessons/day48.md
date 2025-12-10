# Day 48 — The Epoch Loop

**Goal:** Iterate through data multiple times to train weights

An epoch is one complete pass through the training dataset.  Gradient
descent often requires many epochs to minimise the cost.  At each
epoch the algorithm updates the weights based on all examples.  You
track the loss (e.g., MSE) to see if it is decreasing.

## Python Mini‑Lesson

```python
# Train a simple model for several epochs
import numpy as np
X = np.array([[0.2, 0], [0.5, 1], [0.8, 0]])
y = np.array([0.3, 0.8, 0.6])
weights = np.zeros(3)  # two features + bias
eta = 0.1
for epoch in range(50):
    preds = X @ weights[:2] + weights[2]  # linear model
    errors = preds - y
    grad_w = (X.T @ errors) * 2 / len(X)
    grad_b = 2 * errors.mean()
    weights[:2] -= eta * grad_w
    weights[2] -= eta * grad_b
    if (epoch + 1) % 10 == 0:
        mse = (errors ** 2).mean()
        print(f'Epoch {epoch+1}: MSE={mse:.4f}')
```

## Exercises

1. Implement the epoch loop above and observe how the MSE decreases.
2. Try different learning rates and record how they affect convergence.
3. What happens if you shuffle the data between epochs?

## Key Takeaway

Training requires multiple epochs.  Monitoring the loss during the loop tells you whether the model is learning effectively.
