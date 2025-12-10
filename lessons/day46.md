# Day 46 — The Learning Rate (η)

**Goal:** Tune how fast gradient descent moves

The learning rate η controls the size of each update.  Too small and the
algorithm converges slowly; too large and it overshoots or diverges.
Choosing η often requires experimentation.  Some algorithms adjust η
during training to improve convergence.

## Python Mini‑Lesson

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

## Exercises

1. Why does a very large η cause the training to diverge?
2. How can you adapt η over epochs?
3. Name two optimisation algorithms that adjust η automatically.

## Key Takeaway

The learning rate determines the convergence speed and stability of gradient descent.  Proper tuning is essential for successful training.
