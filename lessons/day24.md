# Day 24 — Multiple Regression Concept

**Goal:** Understand fitting a plane instead of a line

## 1. Concept and Definitions

Unlike simple regression, multiple regression fits a plane in a higher
dimensional space.  Each data point has two inputs (ΔT and ΔT×WF) and
one output (t).  The goal is to find coefficients that minimise the
sum of squared errors across all points.  You can solve this using
matrix operations or a library like scikit‑learn.  This lesson
introduces the concept without delving into full linear algebra.

## 2. How to Use It

Apply the concepts above using the formula or algorithm provided. Refer to the mini examples below for a demonstration.

## 3. Why This Matters

Understanding this concept allows you to build more accurate and efficient optimal‑start models, improving comfort and energy savings.

## 4. Mini‑Examples

Here's a simple Python demonstration:

```python
# Fit a simple multiple regression using NumPy
import numpy as np
# Sample data: each row is [ΔT, ΔT×WF]
X = np.array([[4, 4*0.7], [6, 6*0.6], [8, 8*0.8]])
y = np.array([30, 42, 70])
# Add a column of ones for the intercept
X_design = np.column_stack([X, np.ones(len(X))])
# Compute coefficients using the normal equation
coeffs = np.linalg.lstsq(X_design, y, rcond=None)[0]
alpha_a, alpha_b, alpha_d = coeffs
print(f'Coefficients: α₃,a={alpha_a:.2f}, α₃,b={alpha_b:.2f}, α₃,d={alpha_d:.2f}')
```

## 5. Micro‑Exercises

1. Explain why we add a column of ones to the design matrix.
2. Generate your own dataset and fit α₃,a, α₃,b and α₃,d using the code above.
3. Why might fitting Model 3 be difficult directly in a BAS controller without matrix support?
4. Create a simple Python file that performs the calculations from this lesson.
   Use only basic variables, arithmetic, print statements and at most a `for` loop over a list. Avoid defining functions or using `zip`.
   Hint: replicate the structure of the examples above but use your own numbers or dataset.

## 6. Key Takeaway

Multiple regression handles several inputs simultaneously.  The fitted coefficients define a plane that best approximates the observed warm‑up data.
