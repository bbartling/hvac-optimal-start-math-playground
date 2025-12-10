# Day 31 — Calculating the Decay Rate (α₄,c)

**Goal:** Estimate how quickly the error shrinks from logged data

Model 4 requires a decay rate α₄,c between 0 and 1.  One way to
estimate it is to examine how the error (T_sp − T_z) changes minute
over minute.  If e_t and e_{t−1} are consecutive errors, the ratio
e_t/e_{t−1} approximates α₄,c.  Averaging these ratios over a warm‑up
gives a good estimate.

## Python Mini‑Lesson

```python
# Estimate decay rate from error measurements
errors = [8.0, 6.5, 5.0, 3.8, 3.0]  # ΔT values at successive minutes
ratios = [errors[i] / errors[i-1] for i in range(1, len(errors))]
alpha_c = sum(ratios) / len(ratios)
print(f'Estimated decay rate α₄,c = {alpha_c:.2f}')
```

## Exercises

1. Record ΔT every minute during a warm‑up and compute α₄,c.
2. What does α₄,c≈1 imply about the system?
3. Why must α₄,c be less than 1 for heating/cooling?

## Key Takeaway

By averaging successive error ratios you can estimate the decay rate used in Model 4.  It quantifies how quickly the system approaches set point.
