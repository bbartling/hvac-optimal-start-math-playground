# Day 31 — Calculating the Decay Rate (α₄,c)

**Goal:** Show how to estimate the decay factor from historical error data and implement it in Python.

## 1.  Ratio of Successive Errors

In **Model 4** the temperature trajectory is assumed to follow an exponential decay (or rise) towards the setpoint.  If you log the error

```
error_t = T_setpoint - T_zone(t)
```

at each minute during warm‑up, the system’s “decay rate” (called `alpha_c`) is approximated by the average ratio between successive errors:

```
alpha_c ≈ average( error_t / error_{t−1} )
```

A number less than 1 indicates the error is shrinking each minute.

## 2.  Practical Example

Suppose your recorded errors were `[8.0, 6.0, 4.5, 3.3]`.  Compute successive ratios:

* 6 / 8 = 0.75  
* 4.5 / 6 = 0.75  
* 3.3 / 4.5 ≈ 0.73  

The average ratio is roughly **0.74** — this is your estimated `alpha_c`.

## 3.  Python Code

Here’s a small function to estimate the decay factor from a list of errors:

```python
def estimate_decay(errors):
    ratios = [errors[i] / errors[i-1] for i in range(1, len(errors))]
    return sum(ratios) / len(ratios)

errors = [8.0, 6.0, 4.5, 3.3]
alpha_c = estimate_decay(errors)
print(f"Estimated decay: {alpha_c:.2f}")
```

You could extend this by smoothing multiple warm‑up runs together using an EMA on `alpha_c`.

## 4.  Micro‑Exercises

1. Record your own sequence of errors during a warm‑up.  Compute `alpha_c` using the code above.  
2. How does `alpha_c` change on a very cold day vs. a mild day?  
3. Try combining 2–3 days of `alpha_c` estimates with a smoothing factor (e.g., 0.2) to see how the estimate stabilizes.

## 5.  Key Takeaway

The decay rate summarises how quickly the error shrinks.  Accurate estimation requires reliable sensor data and consistent sampling.
