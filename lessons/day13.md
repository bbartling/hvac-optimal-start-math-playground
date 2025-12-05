# Day 13 — Double EMA (EMA of EMA)

**Goal:** Learn how applying an EMA twice can produce extra smoothing and why it’s sometimes used.

In some control applications, especially when data are noisy, a **double EMA** — taking an EMA of an EMA — can provide a smoother trend without losing too much responsiveness.

## 1.  Why Double EMA?

If a single EMA is still too noisy or you have sporadic bad data, a second layer of smoothing dampens fluctuations.  The first EMA filters out high‑frequency noise; the second EMA smooths the filtered series.

## 2.  How It Works

Assume you have a series of observed values `x_t`.  Define:

```
EMA1_t = EMA1_{t−1} + alpha1 * (x_t − EMA1_{t−1})
EMA2_t = EMA2_{t−1} + alpha2 * (EMA1_t − EMA2_{t−1})
```

The second EMA (`EMA2`) reacts even more slowly than the first.  In practice, α values are often the same for both layers.

## 3.  Practical Considerations

* A double EMA can help when sensors are noisy or when you see occasional outliers.
* It delays the response further, so use it only when necessary.
* Niagara’s Optimal Start typically uses a single EMA for degrees‑per‑minute, but understanding the double EMA concept builds intuition for smoothing techniques.

## Mini‑Exercises

1. Start with `EMA1_0 = 10` and `EMA2_0 = 10`, α = 0.2.  The next two observed values are 14 and 9.  Compute `EMA1_1`, `EMA2_1`, `EMA1_2` and `EMA2_2`.
2. Compare `EMA1_2` and `EMA2_2`.  Which is smoother (closer to the initial value)?

## Key Takeaway

A double EMA adds a second layer of smoothing by averaging an average.  It’s rarely required for optimal start, but knowing it helps you understand other smoothing techniques used in controls and data science.