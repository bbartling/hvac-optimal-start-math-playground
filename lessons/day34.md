# Day 34 — Coding Model 4

**Goal:** Implement the logarithmic formula safely

Implementing Model 4 requires careful handling of logs.  You must avoid
taking the logarithm of zero or negative numbers.  Ensure ΔT > 0 and
decay_rate < 1.  If ΔT is within the deadband, you can return zero
runtime (already at set point).

## Python Mini‑Lesson

```python
# Safe computation of Model 4
import math
def model4_time(delta_t, deadband, decay_rate):
    if delta_t <= deadband:
        return 0.0
    if not (0 < decay_rate < 1):
        raise ValueError('decay_rate must be between 0 and 1')
    return math.log(deadband / delta_t) / math.log(decay_rate)

print(model4_time(5.0, 0.5, 0.8))
```

## Exercises

1. Modify the function to handle heating and cooling modes separately with different deadbands.
2. What happens if you pass decay_rate=1?  Why is this invalid?
3. Integrate this function into a control loop that stops heating when t=0.

## Key Takeaway

Robust code for Model 4 checks inputs and handles edge cases.  Careful implementation prevents mathematical errors.
