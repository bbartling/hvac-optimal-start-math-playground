# Day 11 — EMA vs. Raw Average

**Goal:** Compare the exponential moving average to a simple arithmetic mean and understand why EMA is preferred for optimal start.

A raw (arithmetic) average treats all values equally.  An EMA discounts older values and emphasises recent ones.  This difference matters when your building behaviour changes.

## 1.  Raw Average

If you have warm‑up rates 0.20, 0.18, 0.22, 0.25 (°F/min), the raw average is:

```
average = (0.20 + 0.18 + 0.22 + 0.25) / 4 = 0.2125 °F/min
```

This value will change only when you drop an old observation and add a new one.

## 2.  EMA

Using α = 0.3 and starting with 0.20, the EMA after the same sequence becomes:

```
EMA_1 = 0.20 + 0.3 * (0.18 − 0.20) = 0.194
EMA_2 = 0.194 + 0.3 * (0.22 − 0.194) ≈ 0.2018
EMA_3 = 0.2018 + 0.3 * (0.25 − 0.2018) ≈ 0.2153
```

Notice how the EMA moves toward the higher recent values more quickly than a raw average would.  If tomorrow’s observation drops sharply, the EMA will move down accordingly.

## 3.  Why EMA Wins in BAS

* **Responsiveness:** Building performance drifts; the EMA reacts sooner.
* **Memory efficiency:** You only store one value (the current EMA), not a list of past warm‑ups.
* **Tuning:** The α parameter lets you decide how much weight to give new data.

## Mini‑Exercises

1. Compute the raw average of the rates 0.16, 0.19, 0.23, 0.21.
2. Starting with an EMA of 0.16 and α = 0.25, update the EMA with 0.19, then 0.23, then 0.21.
3. Compare the final EMA to the raw average.  Which reflects the latest trend more?

## Key Takeaway

The EMA is better suited to adaptive HVAC control because it adjusts more quickly to changes.  A raw average can lag behind when your building performance improves or degrades.