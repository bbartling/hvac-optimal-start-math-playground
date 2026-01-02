# Day B4 — Solving Linear Systems (Gaussian Elimination)

**Goal:** Solve Aβ = b without math libraries.

## 1. Concept and Definitions

Model 3 solves:

    (XᵀX)β = Xᵀy

Gaussian elimination removes variables step‑by‑step until the system can be solved.

## 2. How to Use It

Steps:
1. Eliminate variables row‑by‑row
2. Back‑substitute to compute coefficients

## 3. Why This Matters

Gaussian elimination is stable and portable across languages.

## 4. Mini‑Example

```python
A = [[3,2,1],[2,3,1],[1,1,2]]
b = [1,2,3]

# forward elimination + back substitution
```

## 5. Micro‑Exercises

1. Solve a 3×3 system by hand.
2. What happens if a pivot is zero?
3. Why is this preferred over determinants?
4. Implement a 3×3 Gaussian solver.

## 6. Key Takeaway

Gaussian elimination is the workhorse of regression solvers.
