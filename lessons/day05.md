# Day 5 — Tuning the Alpha (α)

**Goal:** Explore how changing the smoothing factor affects learning speed and stability.

## 1. Slow vs. Fast Learning

* **Small α (e.g., 0.1):** Each new data point only moves the EMA a little.  This keeps predictions stable but can lag behind sudden changes.
* **Large α (e.g., 0.9):** The EMA almost becomes the current value.  The model learns quickly but may react to noise.

## 2. Visualizing the Difference

Try plotting EMAs with different alphas on the same dataset.  You’ll see one line smoothing softly and another hugging the raw data.

```python
data = [0.3, 0.4, 0.2, 0.5, 0.25]
ema_slow = 0.25
ema_fast = 0.25
alpha_slow, alpha_fast = 0.1, 0.7
for x in data:
    ema_slow = update_ema(ema_slow, x, alpha_slow)
    ema_fast = update_ema(ema_fast, x, alpha_fast)
    print(f"Slow: {ema_slow:.3f}, Fast: {ema_fast:.3f}")
```

## 3. Practical Advice

In HVAC, typical α values are between 0.1 and 0.3.  Start conservative and increase if predictions lag.

## 4. Exercise

Use the `update_ema()` function to compare α = 0.2 and α = 0.6 on the rates [0.18, 0.24, 0.16, 0.30].

## 5. Key Takeaway

Tuning α is balancing speed and stability.  Find a sweet spot for your building.
