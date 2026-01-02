# Day B3 — Matrix Multiplication

**Goal:** Multiply matrices using loops only.

## 1. Concept and Definitions

Matrix multiplication is defined as:

    row × column → single value

Each output entry is a dot product.

## 2. How to Use It

Model 3 requires:
- XᵀX
- Xᵀy

Both are matrix multiplications.

## 3. Why This Matters

If you can multiply matrices, you can implement regression in any language.

## 4. Mini‑Example

```python
A = [[1, 2], [3, 4]]
B = [[5], [6]]

C = [[0]]
for i in range(2):
    C[0][0] += A[0][i] * B[i][0]

print(C)
```

## 5. Micro‑Exercises

1. Multiply a 2×3 by a 3×1 matrix.
2. What happens if dimensions don’t match?
3. Where does matrix multiplication appear in Model 3?
4. Write a general matmul loop.

## 6. Key Takeaway

Matrix multiplication is structured dot products.
