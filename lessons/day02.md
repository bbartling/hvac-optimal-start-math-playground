# Day 2 — The Formula: t = ΔT / rate

**Goal:** Use the simplest linear formula to estimate warm‑up time

When the rate of temperature change is roughly constant, the warm‑up time
(t) can be approximated by dividing the temperature difference by the rate:

t = ΔT / rate.

This equation is simply a rearrangement of the definition of rate.  It is the
basis of the PNNL Model 0 (linear EMA).  In practice you compute ΔT from
the current conditions and divide by a smoothed rate (see the following
lessons) to avoid jitter.

## Python Mini‑Lesson

```python
# Predict warm‑up time using t = ΔT / rate
delta_t = 5.0   # degrees F
rate = 0.20     # degrees per minute
time_est = delta_t / rate
print(f'Predicted time = {time_est:.1f} minutes')
```

## Exercises

1. If ΔT = 8 °F and the rate is 0.25 °F/min, compute the predicted warm‑up time.
2. A building warms 10 °F in 40 minutes.  Predict the time to warm 6 °F assuming the same rate.
3. Explain why simply dividing by today’s rate may lead to poor predictions on some days.

## Key Takeaway

Dividing ΔT by the warm‑up rate gives a quick estimate of run time.  It’s the starting point for more advanced models.
