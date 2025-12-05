# Day 2 — The Formula: t = ΔT / Rate

**Goal:** Understand the raw math behind Model 0 and how to predict runtime once you know the speed.

## 1. Revisiting ΔT and Rate

From Day 1, recall:

```
DeltaT = T_setpoint - T_zone,start
Rate   = DeltaT / DeltaTime
```

## 2. Linear Prediction

Model 0 assumes the zone heats at a constant rate.  To estimate the warm‑up time, simply divide the temperature difference by the learned rate:

```
t = DeltaT / Rate
```

In Python you could write:

```python
def predict_linear(delta_t, rate):
    if rate <= 0:
        return 0
    return delta_t / rate

print(predict_linear(5.0, 0.2))  # 25 minutes
```

## 3. When Linear Works and Fails

This simple formula works well for mild climates or small deltas.  It fails when the heating power changes during the warm‑up (e.g., the last few degrees take longer).  Later models address these cases.

## 4. Exercise

1. Predict the warm‑up time for ΔT = 8 °F with a rate of 0.15 °F/min.
2. Write a Python function `predict_linear(delta_t, rate)` and test it with your own values.

## 5. Key Takeaway

The simplest optimal‑start model is just **division** — but reality is rarely that simple.
