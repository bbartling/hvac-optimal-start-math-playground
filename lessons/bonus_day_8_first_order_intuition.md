# Day B8 — First‑Order Response (Intuition)

**Goal:** Build the mental model for **first‑order response**: the temperature “error” shrinks by the **same percentage** each sample.

> Model 4 in the paper uses a simple first‑order response model to predict the time to reach setpoint. fileciteturn2file1L170-L184

---

## 1) The One Idea

Define the **error**:

- **Cooling:** `error = (T_zone - T_sp)`  
- **Heating:** `error = (T_sp - T_zone)`

Either way: **error is how far you are from setpoint** (in °F).

A first‑order response says:

> “Every time step, error gets multiplied by the same number.”

That is:

```
e_next = c * e_now
```

- If `0 < c < 1` → error decays (good)
- If `c = 1` → no progress (bad)
- If `c > 1` → error grows (very bad / wrong sign)

---

## 2) Why HVAC Feels Like This

When an RTU starts, the first few minutes often have “big progress”, then it slows down near setpoint.

That “slow down” can be approximated by:

- **percentage improvement per minute**
- rather than **constant degrees per minute**

This is why first‑order response often looks “more realistic” than linear models.

---

## 3) Tiny Python (no NumPy)

Run this and watch the error shrink:

```python
from scripts.helpers import simulate_first_order_errors

errors = simulate_first_order_errors(e0=6.0, c=0.90, steps=10)
for i, e in enumerate(errors):
    print(f"minute {i:02d}: error={e:.3f}°F")
```

---

## 4) Micro‑Exercises (5–10 minutes)

1) Try `c=0.95` vs `c=0.85`. Which one reaches setpoint faster?  
2) If the error starts at 8°F, what does “10% improvement per minute” mean?  
3) In your own words: why does a first‑order model slow down near setpoint?

---

## 5) Key Takeaway

**First‑order response = “error shrinks by a constant ratio each step.”**
