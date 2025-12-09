# Day 46 — The Learning Rate ($\eta$)

**Goal:** Write the Python line that actually updates the brain of the model.

## 1. The Learning Rate ($\eta$)

If the gradient says "Move Left," we don't want to jump 1,000 feet. We might overshoot the bottom of the valley. We take a tiny step. This step size is called the **Learning Rate** (usually 0.01 or 0.001).

## 2. The Update Rule

This is the most famous line of code in Machine Learning:

```python
weight = weight - (learning_rate * gradient)
```

  * **Minus sign:** We always move *opposite* the slope (downhill).
  * **Learning Rate:** Controls stability. Too big = unstable. Too small = takes forever to learn.

## 3. Micro‑Exercises

1.  Python Playground:
    ```python
    weight = 5.0
    gradient = 200.0  # From Day 45
    lr = 0.01         # Learning Rate

    # Perform one update
    weight = weight - (lr * gradient)
    print(weight)
    ```
2.  Did the weight move in the correct direction (closer to the true answer)?
3.  Try changing `lr` to 1.0. What happens? (Explosion\!).

## 4. Key Takeaway

The Learning Rate is the "throttle" of your AI. It requires tuning—just like a PID loop\!

