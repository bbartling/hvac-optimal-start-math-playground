# Day B5 — Determinants & Cramer’s Rule

**Goal:** Understand how early Model 3 tutorials solved regression.

## 1. Concept and Definitions

Cramer’s Rule solves linear systems using determinants.

It works well for learning but scales poorly.

## 2. How to Use It

Replace columns of XᵀX with Xᵀy and divide determinants.

## 3. Why This Matters

This explains *why* earlier tutorial code works.

## 4. Mini‑Example

```python
def det3(m):
    return (
        m[0][0]*m[1][1]*m[2][2]
      + m[0][1]*m[1][2]*m[2][0]
      + m[0][2]*m[1][0]*m[2][1]
      - m[0][2]*m[1][1]*m[2][0]
      - m[0][0]*m[1][2]*m[2][1]
      - m[0][1]*m[1][0]*m[2][2]
    )
```

## 5. Micro‑Exercises

1. Compute a determinant by hand.
2. What happens when det ≈ 0?
3. Why does noise break Cramer’s Rule?
4. Implement determinant logic.

## 6. Key Takeaway

Cramer’s Rule teaches regression mechanics but does not scale.
