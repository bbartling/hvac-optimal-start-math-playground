# Day 43 — Algebra vs. Iteration

**Goal:** Distinguish closed‑form solutions from iterative learning

Earlier models used algebraic formulas to solve for coefficients directly.
Machine learning methods like gradient descent instead start with
guesses and iteratively nudge the parameters to reduce error.  This
lesson outlines the conceptual difference between analytical solutions
and iterative optimisation.

## Python Mini‑Lesson

```python
# Simple illustration: solve 2x + 1 = 0
# Algebraic solution
x_exact = -1/2
# Iterative solution using gradient descent on f(x)=2x+1
x = 0.0
learning_rate = 0.1
for _ in range(10):
    grad = 2  # derivative of 2x+1 w.r.t x
    x = x - learning_rate * grad
print(f'Algebraic x={x_exact}, Gradient‑descent x≈{x:.3f}')
```

## Exercises

1. Solve 3x+9=0 algebraically and with gradient descent.
2. Why might you choose an iterative method when a closed‑form exists?
3. Give an example of a problem where an algebraic solution is impossible.

## Key Takeaway

Analytical formulas are exact and fast but may not exist for complex models.  Iterative algorithms approximate solutions when closed forms are unavailable.
