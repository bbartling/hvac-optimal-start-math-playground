# Day 4 — Intro to Exponential Moving Average (EMA)

**Goal:** Learn how smoothing stabilises the rate estimate

To tame the noise seen in daily rate measurements, controllers use an
exponential moving average (EMA).  An EMA takes a fraction (α) of the
difference between the current observation and the previous estimate and
adds it to the old value.  Investopedia describes the general formula for
EMAs as "EMA = current × multiplier + previous EMA × (1 − multiplier)"
【285185230169112†L320-L330】.  For HVAC warm‑up rates this can be
written as:

    new_rate = old_rate + α × (observed_rate − old_rate)

The smoothing factor α (between 0 and 1) determines how quickly the
estimate adapts to new data.  Small α leads to slow changes; large α reacts
quickly but may overreact to noise.

## Python Mini‑Lesson

```python
# Update an EMA of the warm‑up rate
alpha = 0.3
old_rate = 0.20
observed_rate = 0.25
new_rate = old_rate + alpha * (observed_rate - old_rate)
print(f'Old rate     = {old_rate:.2f} °F/min')
print(f'Observed rate = {observed_rate:.2f} °F/min')
print(f'Updated EMA  = {new_rate:.2f} °F/min')
```

## Exercises

1. Starting from a rate of 0.20 °F/min, update the EMA with observed rates of 0.18, 0.22 and 0.16 using α=0.2.
2. Explain how the choice of α affects the balance between responsiveness and stability.
3. Where else are EMAs used in engineering or finance?

## Key Takeaway

An exponential moving average blends new observations with history, smoothing out random fluctuations in the data.
