# Day 18 — Calculating the Base Rate (α₂,a)

**Goal:** Explain how Model 2 first estimates the indoor-only rate before applying weather adjustment.

## 1. Similar to Model 0

Model 2 starts by estimating the indoor warm‑up rate using an EMA, just like Model 0.  Call this `rate_base`.

## 2. Applying the Ratio

After predicting `t_base = DeltaT / rate_base`, multiply it by the weather ratio:

```
t_pred = t_base * Ratio
```

## 3. Example

If `DeltaT = 5 °F`, `rate_base = 0.2 °F/min` → `t_base = 25 min`.  Using the ratio 1.75 from the previous day gives `t_pred = 43.75 min`.

## 4. Key Takeaway

Model 2 still uses a linear indoor model, but it scales the result based on outdoor swings.
