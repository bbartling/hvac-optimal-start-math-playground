# Day 25 — Intro to Matrices (For Technicians)

**Goal:** Get comfortable with matrix notation used in regression

## 1. Concept and Definitions

A matrix is simply a grid of numbers.  In regression we stack our input
vectors into a matrix X and our outputs into a column vector y.  The
normal equation (XᵀX)⁻¹Xᵀy computes the least‑squares coefficients.  You
don’t need to memorise the algebra; it’s more important to recognise
what the shapes mean.  Modern languages (Python, R, MATLAB) perform
these operations with built‑in functions.

## 2. How to Use It

Apply the concepts above using the formula or algorithm provided. Refer to the mini examples below for a demonstration.

## 3. Why This Matters

Understanding this concept allows you to build more accurate and efficient optimal‑start models, improving comfort and energy savings.

## 4. Mini‑Examples

Here's a simple Python demonstration:

```python
# Day 25 - First look at a matrix (just a table of numbers)
import numpy as np

# A is a 2x2 "table"
# Row 0: [1, 2]
# Row 1: [3, 4]
A = np.array([
    [1, 2],
    [3, 4],
])

# B is a 2x1 "column"
# Row 0: [5]
# Row 1: [6]
B = np.array([
    [5],
    [6],
])

# The @ operator means "matrix multiply"
C = A @ B

print("A shape:", A.shape)    # (2, 2)
print("B shape:", B.shape)    # (2, 1)
print("C shape:", C.shape)    # (2, 1)
print()

print("A =")
print(A)
print()

print("B =")
print(B)
print()

print("C = A @ B =")
print(C)

```


**What this does (in words you could put right under the code):**

* Think of `A` as a **2-row by 2-column table**.
* Think of `B` as a **2-row by 1-column table**.
* `C = A @ B` is just “mix these numbers together in a standard way”:

  * Top of `C` = `1*5 + 2*6 = 17`
  * Bottom of `C` = `3*5 + 4*6 = 39`

So you end up with:

```text
C = [[17]
     [39]]
```

That’s all “matrix multiplication” is here: a rule for combining rows of A with the column of B.


## 5. Micro‑Exercises

1. Create two 2×2 matrices and compute their product using @.
2. Why do we use matrix multiplication (XᵀX and Xᵀy) in regression?
3. How does adding a column of ones change the shape of X?
4. Create a simple Python file that performs the calculations from this lesson.
   Use only basic variables, arithmetic, print statements and at most a `for` loop over a list. Avoid defining functions or using `zip`.
   Hint: replicate the structure of the examples above but use your own numbers or dataset.

## 6. Key Takeaway

Matrices provide a compact way to represent and solve linear systems.  Understanding the shapes helps you implement multiple regression.
