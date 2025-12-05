# Day 24 — Multiple Regression Concept

**Goal:** Describe what it means to fit a plane to data and why simple pencil‑and‑paper methods don’t suffice.

## 1. From Line to Plane

With one feature you fit a line.  With two features you fit a plane in 3D space.  The goal is to minimise the squared error between the plane and each data point.

## 2. Why Not Solve by Hand?

Solving for `a`, `b`, and `d` requires inverting a 3×3 matrix of sums.  This is cumbersome and error‑prone with pen and paper.

## 3. Python to the Rescue

Use libraries like `numpy` and `sklearn` to handle the matrix algebra.  It’s one line of code to fit a regression:

```python
import numpy as np
from sklearn.linear_model import LinearRegression

X = np.array([[DeltaT, DeltaT * WF] for DeltaT, WF in data])
y = np.array(minutes)
model = LinearRegression().fit(X, y)
a, b = model.coef_
d = model.intercept_
```

## 4. Key Takeaway

Multiple regression is powerful but requires matrix math.  Use Python’s libraries rather than solving by hand.
