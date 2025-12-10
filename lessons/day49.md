# Day 49 — The Monday Neuron

**Goal:** Interpret the weight for the Monday feature

After training a model that includes a "Monday" indicator feature,
you can interpret the associated weight as the additional minutes needed
on Mondays.  A positive weight means the model learned that Mondays
require extra time.  Reading weights helps you validate that the model
captured the Monday effect correctly.

## Python Mini‑Lesson

```python
# Train a linear model with a Monday feature
import numpy as np
# Features: [scaled_ΔT, is_monday]
X = np.array([[0.3, 0], [0.6, 1], [0.8, 0], [0.4, 1]])
y = np.array([0.4, 0.9, 0.7, 0.6])
# Add bias column
X_design = np.column_stack([X, np.ones(len(X))])
weights = np.linalg.lstsq(X_design, y, rcond=None)[0]
delta_weight, monday_weight, bias = weights
print(f'Monday weight = {monday_weight:.2f}')
```

## Exercises

1. Use your own dataset with a Monday indicator and interpret the Monday weight.
2. What does a negative Monday weight imply?
3. How could you incorporate a weekend length (e.g., holiday) into the features?

## Key Takeaway

The weight on the Monday feature quantifies the additional minutes needed after a long weekend.  Inspecting weights gives insight into the model’s behaviour.
