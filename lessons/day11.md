# Day 11 — Simple Regression (Line Fitting)

**Goal:** Learn how to fit a straight line through data points to estimate coefficients a and b.

## 1. Regression Basics

To calibrate Model 1, we need to find `a` and `b` such that `t = a * x + b` (where `x = DeltaT**2`) fits the data.  With two data points, you can solve for `a` and `b` exactly.

## 2. Two‑Point Solution

Given (x1, t1) and (x2, t2):

```
a = (t2 - t1) / (x2 - x1)
b = t1 - a * x1
```

## 3. Python Example

```python
def solve_two_point(x1, t1, x2, t2):
    a = (t2 - t1) / (x2 - x1)
    b = t1 - a * x1
    return a, b

# Example: (4, 10) and (25, 40)
print(solve_two_point(4,10,25,40))  # (1.0, 6.0)
```

## 4. Key Takeaway

You don’t need fancy tools to estimate a quadratic model.  Basic algebra and two points will get you there.
