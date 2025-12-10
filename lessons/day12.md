# Day 12 — Solving for a and b (Manual Math)

**Goal:** Apply the OLS formulas to compute Model 1 parameters

Given a series of (ΔT², t) pairs, you can compute the optimal α₁,a and
α₁,b using the same regression formulas from Day 11.  Here x = (ΔT)² and
y = t.  The resulting coefficients minimise the sum of squared errors
between the quadratic model and the data.  Writing out the sums by hand
reinforces the algebraic process.

## Python Mini‑Lesson

```python
# Example data: (ΔT, time) pairs
deltas = [3, 5, 7]
times = [20, 38, 60]
xs = [d ** 2 for d in deltas]
ys = times
n = len(xs)
sum_x = sum(xs)
sum_y = sum(ys)
sum_xy = sum(x * y for x, y in zip(xs, ys))
sum_x2 = sum(x * x for x in xs)

alpha_a = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
alpha_b = (sum_y - alpha_a * sum_x) / n
print(f'α₁,a={alpha_a:.2f} min/°F², α₁,b={alpha_b:.2f} min')
```

## Exercises

1. Choose your own (ΔT, t) pairs and compute α₁,a and α₁,b.
2. Verify that substituting the computed coefficients into t=α₁,a·(ΔT)²+α₁,b
reduces the error for your dataset.
3. Why is it important to use several days of data rather than a single observation?

## Key Takeaway

Manually calculating α₁,a and α₁,b gives you insight into how quadratic models are fitted.  With more data the estimates become more reliable.
