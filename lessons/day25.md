# Day 25 — Intro to Matrices (For Technicians)

**Goal:** Demystify matrices and show how they are used in Model 3’s regression.

## 1. What Is a Matrix?

A matrix is just a table of numbers.  In regression we arrange our features into a matrix `X` and our target into a vector `y`.

## 2. Example Matrix

For three datapoints with features x1 and x2:

```
X = [[x1_1, x2_1],
     [x1_2, x2_2],
     [x1_3, x2_3]]

y = [t1, t2, t3]
```

## 3. Solving the System

Model 3 finds coefficients `w = [a, b]` and `d` such that `X @ w + d ≈ y`.  Libraries handle this by computing `(Xᵀ X)⁻¹ Xᵀ y` behind the scenes.

## 4. Key Takeaway

Don’t fear matrices.  Think of them as spreadsheets that Python can multiply and invert for you.
