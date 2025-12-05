# Day 3 — The Noise Problem

**Goal:** Learn why using only today’s rate leads to jittery control and why averaging is needed.

## 1. Why One Day Isn’t Enough

A single day’s rate can be misleading.  Maybe a door was propped open or the equipment cycled unexpectedly.  If you base tomorrow’s prediction solely on today, you’ll get **jittery start times**.

## 2. Variability Example

Suppose you record these rates over three days: 0.25, 0.12, 0.35 °F/min.  Which one should you pick for tomorrow?  Clearly the building’s performance fluctuates.

## 3. Need for Smoothing

To avoid chasing noise, we **smooth** the past data.  The next lesson introduces the **Exponential Moving Average (EMA)**, which weights recent data more than old data but still smooths out randomness.

## 4. Exercise

Create a list of observed rates, then calculate a simple average (mean).  Compare how the mean differs from the last value.

```python
rates = [0.25, 0.12, 0.35]
avg_rate = sum(rates) / len(rates)
print(avg_rate)  # 0.24
```

## 5. Key Takeaway

Basing predictions on a single day’s data leads to unstable schedules.  A smoothing method is required.
