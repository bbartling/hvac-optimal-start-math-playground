# Day 32 — The Coast‑to‑Stop Effect

**Goal:** Explain why heating slows as set point nears

As the zone temperature approaches the set point, the driving force for
heat transfer diminishes.  The coil may also modulate or cycle off
to prevent overshoot.  This leads to the ‘coast‑to‑stop’ effect
captured by Model 4.  The logarithmic formula accounts for this
slowing by predicting longer times near the end of the warm‑up.

## Python Mini‑Lesson

```python
# Simulate temperature approach using a simple decay model
T_sp = 70.0
T = 60.0
alpha_c = 0.85
for minute in range(1, 11):
    error = T_sp - T
    T += error * (1 - alpha_c)  # fractional approach
    print(f'min {minute}: T={T:.2f}°F, error={T_sp - T:.2f}°F')
```

## Exercises

1. What would happen if the coil delivered constant power until set point?
2. Describe two physical reasons why heating slows near set point.
3. How does Model 4 prevent overshooting the target temperature?

## Key Takeaway

The coast‑to‑stop behaviour reflects reduced temperature difference and modulation near set point.  Model 4’s logarithmic form captures this effect.
