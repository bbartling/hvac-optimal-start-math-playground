# Day 3 — The Noise Problem

**Goal:** Recognise that a single day’s rate can be misleading

Real buildings rarely warm at exactly the same speed every day.  Weather,
occupancy, and equipment variations cause the observed rate to bounce
around.  Using only today’s rate may lead to large errors, because the
measurement is noisy.  Instead, controllers smooth the rate over many days
to avoid jitter and overreaction.

You can simulate noise by adding random fluctuations to a ‘true’ rate and
see how the predicted time varies.

## Python Mini‑Lesson

```python
import random
true_rate = 0.2  # °F/min
noisy_rates = [true_rate + random.uniform(-0.05, 0.05) for _ in range(5)]
delta_t = 5.0
for i, r in enumerate(noisy_rates, 1):
    t_est = delta_t / r
    print(f'Day {i}: rate={r:.3f} → t≈{t_est:.1f} min')
```

## Exercises

1. Run the script several times.  How much does the predicted time change?
2. Why might yesterday’s warm‑up rate be different from today’s?
3. Describe two factors that could cause noisy warm‑up data in buildings.

## Key Takeaway

Relying on a single noisy measurement leads to unpredictable predictions.  Smoothing the rate over time reduces this noise.
