# Day B12 — Compute Model 4 t_opt from a Real Startup Window

**Goal:** From a short “after startup” window, estimate `c`, then compute `t_opt`.

Model 4’s time formula uses `ln(a/b) / ln(c)` with:
- `a` deadband
- `b` initial error
- `c` learned decay ratio fileciteturn2file1L170-L184

---

## 1) The Minimal Data You Need

Right after you start the unit, collect a small batch:

- `T_sp`
- `T_zone` each sample (ex: 1 minute interval)

Convert to errors:

```
e_i = T_sp - T_zone_i   (heating form)
e_i = T_zone_i - T_sp   (cooling form)
```

Pick **one sign convention** and stick to it.

---

## 2) Compute t_opt

1) `b = e0` (initial error)  
2) estimate `c` from the window  
3) choose deadband `a`  
4) compute:

```
t_opt = ln(a/|b|) / ln(c)
```

---

## 3) Tiny Python (no NumPy)

```python
from scripts.helpers import estimate_c_least_squares, model4_topt_minutes

deadband = 0.5
errors = [6.0, 5.3, 4.7, 4.2, 3.8, 3.4]  # after startup

c = estimate_c_least_squares(errors)
t = model4_topt_minutes(deadband_deg=deadband, e0=errors[0], c=c)

print("c:", c)
print("t_opt:", t, "minutes")
```

---

## 4) Micro‑Exercises

1) Try deadband 1.0°F vs 0.25°F and compare runtime.  
2) Try a “bad day” where errors barely change. What does the model predict?  
3) If c is estimated slightly too high (closer to 1), does t_opt grow or shrink?

---

## 5) Key Takeaway

Model 4 is: **learn decay**, then **solve time-to-deadband**.
