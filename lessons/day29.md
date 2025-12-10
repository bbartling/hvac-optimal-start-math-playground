# Day 29 — Thinking Like a Capacitor

**Goal:** Conceptualise buildings as thermal capacitors

In electrical engineering a capacitor charges and discharges exponentially.
Buildings behave similarly: they warm quickly at first and then slow as
they approach set point.  This analogy leads to logarithmic models
where the time to reduce the error follows t ∝ ln(E0/E).  Recognising
this behaviour prepares you for Model 4.

## Python Mini‑Lesson

```python
# Simulate exponential charging (analogous to heating)
import math
tau = 10.0  # time constant
time_values = [0, 5, 10, 20]
for t in time_values:
    fraction = 1 - math.exp(-t / tau)
    print(f't={t} min → fraction charged={fraction:.3f}')
```

## Exercises

1. What physical properties of a building correspond to a large time constant?
2. If the time constant is small, how does the system behave?
3. Give another real‑world system that follows exponential behaviour.

## Key Takeaway

Thermal processes often mirror exponential charging and discharging.  This insight motivates the logarithmic formula in Model 4.
