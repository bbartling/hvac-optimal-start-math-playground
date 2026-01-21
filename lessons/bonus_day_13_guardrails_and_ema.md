# Day B13 — Guardrails + EMA Smoothing (Make it Production‑Safe)

**Goal:** Stop Model 4 from doing stupid things on noisy days (Monday problem, weird loads, sensor noise).

The paper discusses using EMA-style smoothing for parameter updates (general parameter tuning strategy). fileciteturn2file1L235-L244

---

## 1) The Two Failure Modes

### A) c gets too close to 1
- prediction explodes (very long start time)

### B) c changes day-to-day too much
- start time becomes twitchy

Both happen in real buildings.

---

## 2) Guardrails (simple and effective)

- Clamp `c` into a safe range, like `[0.80, 0.99]`
- Enforce a maximum start time, like 180 minutes
- Require at least N samples before trusting an estimate
- If the error slope goes the wrong way, mark “bad data day”

These aren’t “math”. They’re “don’t wake the building manager”.

---

## 3) EMA Smoothing for c

If you estimate a daily `c_new`, smooth it:

```
c_ema = c_ema + w * (c_new - c_ema)
```

This is the same update idea used for parameters in the paper. fileciteturn2file1L235-L244

---

## 4) Tiny Python (no NumPy)

```python
from scripts.helpers import ema, clamp

c_ema = 0.92
w = 0.30  # learning weight

daily_estimates = [0.90, 0.94, 0.98, 0.91, 0.88]  # noisy
for c_new in daily_estimates:
    c_new = clamp(c_new, 0.80, 0.99)
    c_ema = ema(c_ema, c_new, w)
    print("c_ema:", round(c_ema, 4))
```

---

## 5) Micro‑Exercises

1) Increase w to 0.8. What happens to stability?  
2) Decrease w to 0.1. What happens to responsiveness?  
3) What guardrail prevents “start 6 hours early”?

---

## 6) Key Takeaway

**A stable model beats a perfect model.**
