# Day 13 — Self‑Tuning Model 1

**Goal:** Apply EMA to the coefficients a and b so the quadratic model learns over time.

## 1. Why Tune Coefficients?

Building behaviour changes seasonally.  Rather than refitting `a` and `b` from scratch every day, you can blend the newest estimates into the existing coefficients.

## 2. EMA on Coefficients

```
a_new = a_old + ω * (a_today - a_old)
b_new = b_old + ω * (b_today - b_old)
```

where `ω` is a small learning rate (e.g., 0.1).

## 3. Python Example

```python
def update_coeff(old, new_estimate, weight):
    return old + weight * (new_estimate - old)

a_old, b_old = 0.5, 7
a_today, b_today = 0.6, 6.5
weight = 0.1
a_new = update_coeff(a_old, a_today, weight)
b_new = update_coeff(b_old, b_today, weight)
print(a_new, b_new)
```

## 4. Key Takeaway

EMA doesn’t just smooth temperatures; it can smooth model parameters too, allowing Model 1 to adjust gradually to new data.
