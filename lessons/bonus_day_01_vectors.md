# Day B1 — Vectors & Dot Products

**Goal:** Understand vectors as simple lists and learn the dot product — the core building block of all matrix math.

## 1. Concept and Definitions

A **vector** is just an ordered list of numbers.

In optimal start math, vectors represent:
- temperature errors over time
- model coefficients
- rows and columns inside matrices

The **dot product** combines two vectors into a single number:

    dot(a, b) = a₁b₁ + a₂b₂ + …

This operation shows up everywhere in prediction and regression.

## 2. How to Use It

Any time you see a weighted sum like:

    t = d + a·ΔT + b·(ΔT·WF)

you are computing a dot product.

## 3. Why This Matters

Matrix multiplication is nothing more than repeated dot products.  
If this lesson clicks, Model 3 becomes mechanical instead of mysterious.

## 4. Mini‑Example

```python
a = [1, 2, 3]
b = [4, 5, 6]

dot = 0
for i in range(len(a)):
    dot += a[i] * b[i]

print(dot)  # 32
```

## 5. Micro‑Exercises

1. Compute the dot product of `[2, 4]` and `[10, 1]`.
2. Why must vectors be the same length?
3. Where does the dot product appear in Model 3?
4. Write your own dot‑product script using a loop only.

## 6. Key Takeaway

Dot products are the atomic unit of regression math.
