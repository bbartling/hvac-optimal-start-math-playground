# Day B10 — Deadband (Comfort) vs Runtime

**Goal:** Understand the **deadband** (acceptable remaining error) and why Model 4 needs it.

In the paper, Model 4 uses a constant parameter representing an acceptable deadband from setpoint. fileciteturn2file1L170-L184

---

## 1) Deadband in Plain English

A thermostat rarely targets a single exact number.

It targets a **range** like:

- cooling: 74°F ± 1°F
- heating: 70°F ± 1°F

That ± range is the deadband / hysteresis zone.

For optimal start, deadband means:

> “I’m done preconditioning when the zone is within `a` degrees of setpoint.”

---

## 2) How Deadband Enters Model 4

Model 4 time equation uses:

- `a` = deadband (how close is “good enough”)
- `b` = initial error at start
- `c` = error decay ratio

t_opt becomes larger when:
- deadband `a` is tighter (smaller)
- initial error `b` is bigger
- decay ratio `c` is weaker (closer to 1)

That’s exactly the “longer/shorter start time” behavior described in the paper. fileciteturn2file1L170-L184

---

## 3) Tiny Python (no NumPy)

```python
from scripts.helpers import model4_topt_minutes

for a in (1.0, 0.5, 0.25):
    t = model4_topt_minutes(deadband_deg=a, e0=6.0, c=0.90)
    print(f"deadband={a}°F -> t_opt={t:.1f} minutes")
```

---

## 4) Micro‑Exercises

1) If your site complains about “late to setpoint”, do you make deadband bigger or smaller?  
2) If your site complains about “starts too early”, what deadband change might help?  
3) Why is deadband a *policy decision* and not just “math”?

---

## 5) Key Takeaway

Deadband is where **comfort policy** meets **runtime math**.
