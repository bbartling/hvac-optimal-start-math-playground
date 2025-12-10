# Day 46 — The Learning Rate (η)

**Goal:** Tune how fast gradient descent moves

## 1. Concept and Definitions

The learning rate η controls the size of each update.  Too small and the
algorithm converges slowly; too large and it overshoots or diverges.
Choosing η often requires experimentation.  Some algorithms adjust η
during training to improve convergence.

## 2. How to Use It

Apply the concepts above using the formula or algorithm provided. Refer to the mini examples below for a demonstration.

## 3. Why This Matters

Understanding this concept allows you to build more accurate and efficient optimal‑start models, improving comfort and energy savings.

## 4. Mini‑Examples

Here's a simple Python demonstration:

```python
# Demonstrate different learning rates
x_data = [1, 2, 3]
y_actual = [2, 4, 6]
for eta in [0.01, 0.1, 0.5]:
    w = 0.0
    for _ in range(20):
        grad = sum((w * x - y) * x for x, y in zip(x_data, y_actual)) * 2 / len(x_data)
        w = w - eta * grad
    print(f'η={eta} → final w≈{w:.2f}')
```

## 5. Micro‑Exercises

1. Why does a very large η cause the training to diverge?
2. How can you adapt η over epochs?
3. Name two optimisation algorithms that adjust η automatically.
4. Create a simple Python file that performs the calculations from this lesson.
   Use only basic variables, arithmetic, print statements and at most a `for` loop over a list. Avoid defining functions or using `zip`.
   Hint: replicate the structure of the examples above but use your own numbers or dataset.

## 6. Key Takeaway

The learning rate determines the convergence speed and stability of gradient descent.  Proper tuning is essential for successful training.
