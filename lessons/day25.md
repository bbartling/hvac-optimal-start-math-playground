# Day 25 — Intro to Matrices (For Technicians)

**Goal:** Get comfortable with matrix notation used in regression

A matrix is simply a grid of numbers.  In regression we stack our input
vectors into a matrix X and our outputs into a column vector y.  The
normal equation (XᵀX)⁻¹Xᵀy computes the least‑squares coefficients.  You
don’t need to memorise the algebra; it’s more important to recognise
what the shapes mean.  Modern languages (Python, R, MATLAB) perform
these operations with built‑in functions.

## Python Mini‑Lesson

```python
# Demonstrate basic matrix multiplication
import numpy as np
A = np.array([[1, 2], [3, 4]])
B = np.array([[5], [6]])
product = A @ B
print('Matrix A:
', A)
print('Vector B:
', B)
print('A @ B =
', product)
```

## Exercises

1. Create two 2×2 matrices and compute their product using @.
2. Why do we use matrix multiplication (XᵀX and Xᵀy) in regression?
3. How does adding a column of ones change the shape of X?

## Key Takeaway

Matrices provide a compact way to represent and solve linear systems.  Understanding the shapes helps you implement multiple regression.
