# Day B14 — Model 4 End‑to‑End (Pure Python Mini Version)

**Goal:** Implement a runnable “mini Model 4” loop:
1) build errors from samples
2) estimate `c`
3) compute `t_opt`
4) apply guardrails + EMA

Model 4 uses:
- log expression for time (Eq. 21) fileciteturn2file1L170-L184
- least-squares style estimate for c (Eq. 23 structure) fileciteturn2file1L170-L184
- EMA idea for parameter stability fileciteturn2file1L235-L244

---

## 1) What This Mini Script Demonstrates

- Why `c` is a “system strength” number
- How deadband affects runtime
- How to keep your logic stable enough for real HVAC

---

## 2) Run the Script

```bash
python scripts/dayF7_model4_end_to_end.py
```

---

## 3) Micro‑Exercises

1) Change deadband from 0.5°F to 0.25°F. Observe runtime.  
2) Increase noise and see how EMA helps.  
3) Force a “bad day” by using c close to 1. What guardrail saves you?

---

## 4) Key Takeaway

Model 4 is the simplest “physics-ish” model in the set:
**learn first‑order decay → solve time-to-deadband → stabilize with EMA.**
