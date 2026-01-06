# Day F4 — Estimating the “c” Parameter from Real Data

**Goal:** Estimate the first‑order decay ratio `c` from a batch of error samples after startup.

The paper estimates `c` using a least‑squares style ratio of error terms (Eq. 23). fileciteturn2file1L170-L184

---

## 1) What is “c” Again?

If your error sequence after startup is:

```
e0, e1, e2, e3, ...
```

First‑order behavior means:

```
e1 ≈ c * e0
e2 ≈ c * e1
...
```

So `c` is basically the **typical ratio** between consecutive errors.

---

## 2) Why You Don’t Just Use e1/e0

Because real data is noisy.

So Model 4 uses a batch of N samples to estimate a single “best” c.

The least squares ratio looks like:

```
c = sum(e_{i-1} * e_i) / sum(e_{i-1}^2)
```

This matches the structure in Eq. (23) (discrete-time form). fileciteturn2file1L170-L184

---

## 3) Tiny Python (no NumPy)

```python
from scripts.helpers import estimate_c_least_squares

errors = [6.0, 5.4, 4.9, 4.3, 3.9]  # example after startup
c_hat = estimate_c_least_squares(errors)
print("estimated c:", c_hat)
```

Interpretation:
- `c_hat` near 0.85 → strong system (fast improvement)
- `c_hat` near 0.97 → weak system (slow improvement)

---

## 4) Micro‑Exercises

1) Try the same errors but add noise (jitter). Does the estimate stay reasonable?  
2) Try an example where errors stop improving (flat). What does `c_hat` become?  
3) What happens if errors change sign because you defined heating/cooling wrong?

---

## 5) Key Takeaway

Model 4 learns system “strength” from the **trend of error decay**, not from a single slope.
