# Day B9 — Exponentials, Logs, and “Time to Target”

**Goal:** Learn why Model 4 uses **logs** to solve “how many minutes until we’re close enough?”

Model 4 computes optimal start time with a closed form log expression. fileciteturn2file1L170-L184

---

## 1) From Repeated Multiplication to Exponential

If:

```
e_1 = c * e_0
e_2 = c * e_1 = c^2 * e_0
...
e_n = c^n * e_0
```

That’s an exponential decay (for 0 < c < 1).

---

## 2) What We Want in Optimal Start

We don’t need “perfect” setpoint.

We need “close enough”, i.e. within a **deadband**:

```
|e_n| <= a
```

- `a` = acceptable error (deadband) in °F
- `e_0` = initial error at start time
- `c` = decay ratio per sample

Solve:

```
|c^n * e_0| <= a
```

Take logs to isolate `n`:

```
n >= ln(a/|e0|) / ln(c)
```

That matches the paper’s structure for Model 4 optimal start time. fileciteturn2file1L170-L184

---

## 3) Tiny Python (no NumPy)

```python
import math

a = 0.5     # deadband °F
e0 = 6.0    # initial error °F
c = 0.90    # decay ratio per minute

n = math.log(a / abs(e0)) / math.log(c)
print("minutes needed:", n)
```

If `c` is close to 1, `ln(c)` is a small negative number → **long time**.

---

## 4) Micro‑Exercises

1) If you tighten deadband from 1°F to 0.25°F, does time go up or down? Why?  
2) What happens if you accidentally estimate `c=1.02`?  
3) Why is `ln(c)` negative for a good decaying system?

---

## 5) Key Takeaway

Model 4 is basically: **how long until the decaying error is smaller than the deadband?**
