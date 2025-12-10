# Day 1 — The Basics: ΔT and Rate

**Goal:** Understand temperature difference and rate of change in HVAC warm‑up

Optimal start begins with two simple quantities: the temperature difference (ΔT)
between the desired set point and the current zone temperature, and the rate
at which the zone warms or cools.  ΔT is just subtraction, and the rate is
computed as ΔT divided by the time it took to achieve that change.  Knowing
both quantities allows you to predict how long the system needs to run to
reach set point.

In HVAC, we often express the rate in degrees per minute (°F/min).  A small
ΔT with a slow rate results in a longer preheat, while a large ΔT with a
rapid rate leads to a shorter preheat.

## Python Mini‑Lesson

```python
# Compute ΔT and rate of change
setpoint = 72.0
zone_start = 65.0
delta_t = setpoint - zone_start  # degrees F

time_minutes = 35
rate = delta_t / time_minutes  # degrees per minute

print(f'DeltaT = {delta_t:.1f} °F')
print(f'Rate   = {rate:.3f} °F/min')
```

## Exercises

1. Compute ΔT for a zone at 67 °F with a set point of 74 °F.
2. A zone warms from 64 °F to 72 °F in 30 minutes.  What is the rate of change?
3. If ΔT = 6 °F and the rate is 0.25 °F/min, how many minutes will it take to reach set point?

## Key Takeaway

ΔT and rate are the foundation of all optimal start models.  Without these two numbers, you cannot estimate warm‑up time.
