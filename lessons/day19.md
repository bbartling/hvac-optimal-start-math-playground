# Day 19 — The Double Prediction

**Goal:** Walk through the two-step prediction process of Model 2 and practice with Python.

## 1. Step‑by‑Step

1. Predict base time: `t_base = DeltaT / rate_base`.
2. Compute the weather ratio.
3. Multiply: `t_pred = t_base * ratio`.

## 2. Python Example

```python
def predict_model2(delta_t, rate_base, t_ref, oat_yesterday, oat_today):
    t_base = delta_t / rate_base
    ratio = (t_ref - oat_yesterday) / (t_ref - oat_today)
    return t_base * ratio

print(predict_model2(6, 0.18, 0, 30, 10))  # Example
```

## 3. Key Takeaway

Model 2 is simple to implement in code.  It just introduces a scaling factor to your linear prediction.
