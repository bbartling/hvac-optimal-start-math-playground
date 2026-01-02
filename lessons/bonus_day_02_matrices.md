# Day B2 — Matrices & Transpose

**Goal:** Learn how matrices are represented and why transpose exists.

## 1. Concept and Definitions

A **matrix** is simply a list of vectors (rows):

    X = [
      [1, ΔT, ΔT·WF],
      ...
    ]

The **transpose** flips rows into columns and is written as Xᵀ.

## 2. How to Use It

Transpose is required to compute:
- XᵀX
- Xᵀy

These terms appear in every least‑squares regression.

## 3. Why This Matters

Without transpose, Model 3 regression cannot be computed at all.

## 4. Mini‑Example

```python
X = [
    [1, 2],
    [3, 4],
    [5, 6]
]

XT = []
for c in range(len(X[0])):
    col = []
    for r in range(len(X)):
        col.append(X[r][c])
    XT.append(col)

print(XT)
```

## 5. Micro‑Exercises

1. Transpose a 2×3 matrix by hand.
2. Verify the new dimensions.
3. Why is XᵀX always square?
4. Write your own transpose routine.

## 6. Key Takeaway

Transpose exists to make matrix dimensions compatible — nothing mystical.
