# Day 50 — The Final Boss: Full Custom Engine

**Goal:** Build and train a simple gradient‑descent optimal start model

For the final project you will implement a mini gradient descent engine
that predicts warm‑up time based on scaled ΔT and a Monday flag.  You
will initialise weights, loop over the dataset for many epochs, compute
gradients and update the weights.  When training completes you should
see that the Monday weight is positive, indicating extra time on the
first day of the week.

## Python Mini‑Lesson

```python
# Gradient descent on a small dataset
import numpy as np
# Prepare dataset (scaled ΔT, is_monday) and target times in hours
X = np.array([[0.3, 0], [0.6, 1], [0.8, 0], [0.5, 1], [0.7, 0]])
y = np.array([0.4, 1.0, 0.8, 0.9, 0.7])
weights = np.zeros(3)  # two features + bias
eta = 0.1
for epoch in range(100):
    preds = X @ weights[:2] + weights[2]
    errors = preds - y
    grad_w = (X.T @ errors) * 2 / len(X)
    grad_b = 2 * errors.mean()
    weights[:2] -= eta * grad_w
    weights[2] -= eta * grad_b
# Print final weights
delta_weight, monday_weight, bias = weights
print(f'Weights: ΔT={delta_weight:.2f}, Monday={monday_weight:.2f}, bias={bias:.2f}')
```

## Exercises

1. Replace the dataset with your own data and train the model.
2. Does the Monday weight end up positive?  What does that indicate?
3. How could you extend this model to include outdoor temperature or other features?

## Key Takeaway

Building your own gradient descent model consolidates everything you’ve learned.  The final weights reveal how the algorithm interprets ΔT and Mondays.
