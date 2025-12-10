# Day 50 — The Final Boss: Full Custom Engine

**Goal:** Build and train a simple gradient‑descent optimal start model

## 1. Concept and Definitions

For the final project you will implement a mini gradient descent engine
that predicts warm‑up time based on scaled ΔT and a Monday flag.  You
will initialise weights, loop over the dataset for many epochs, compute
gradients and update the weights.  When training completes you should
see that the Monday weight is positive, indicating extra time on the
first day of the week.

## 2. How to Use It

Apply the concepts above using the formula or algorithm provided. Refer to the mini examples below for a demonstration.

## 3. Why This Matters

Understanding this concept allows you to build more accurate and efficient optimal‑start models, improving comfort and energy savings.

## 4. Mini‑Examples

Here's a simple Python demonstration:

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

## 5. Micro‑Exercises

1. Replace the dataset with your own data and train the model.
2. Does the Monday weight end up positive?  What does that indicate?
3. How could you extend this model to include outdoor temperature or other features?
4. Create a simple Python file that performs the calculations from this lesson.
   Use only basic variables, arithmetic, print statements and at most a `for` loop over a list. Avoid defining functions or using `zip`.
   Hint: replicate the structure of the examples above but use your own numbers or dataset.

## 6. Key Takeaway

Building your own gradient descent model consolidates everything you’ve learned.  The final weights reveal how the algorithm interprets ΔT and Mondays.
