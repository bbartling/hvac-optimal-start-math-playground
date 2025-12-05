# Day 31 — Calculating the Decay Rate (α₄,c)

**Goal:** Show how to estimate the decay factor from historical error data and implement it in Python.

## 1. Ratio of Successive Errors

If `error_t = T_setpoint - T_zone(t)`, then the decay factor `alpha_c` can be estimated as the average of `error_t / error_{t-1}` over a warm‑up run.

## 2. Example

Suppose error measurements were [8, 6, 4.5, 3.3].  Compute ratios: 6/8=0.75, 4.5/6=0.75, 3.3/4.5≈0.73.  The average `alpha_c ≈ 0.74`.

## 3. Python Code

```python
def estimate_decay(errors):
    ratios = [errors[i]/errors[i-1] for i in range(1, len(errors))]
    return sum(ratios)/len(ratios)

alpha_c = estimate_decay([8,6,4.5,3.3])
print(alpha_c)
```

## 4. Key Takeaway

The decay factor captures how quickly the error shrinks.  Accurate estimation requires good sensor data.
