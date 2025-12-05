# Day 4 — Intro to Exponential Moving Average (EMA)

**Goal:** Introduce EMA as a simple smoothing filter and derive the update formula.

## 1. What Is an EMA?

The **Exponential Moving Average** is a way to smooth a series of data points by giving more weight to recent measurements and less weight to older ones.

The update formula is:

```
EMA_new = EMA_old + α * (Current - EMA_old)
```

where **α (alpha)** is the smoothing factor between 0 and 1.

## 2. Python Implementation

```python
def update_ema(old_ema, current, alpha):
    return old_ema + alpha * (current - old_ema)

ema = 0.20  # initial rate
alpha = 0.3
for current_rate in [0.25, 0.12, 0.35]:
    ema = update_ema(ema, current_rate, alpha)
    print(ema)
```

## 3. Choosing α

* **α small (e.g., 0.1):** Smooths heavily; slow to adapt.
* **α large (e.g., 0.5):** Reacts quickly; may chase noise.

## 4. Exercise

Set `alpha = 0.2` and an initial EMA of 0.18.  Compute the EMA after the sequence [0.15, 0.22, 0.20].

## 5. Key Takeaway

EMA balances stability with responsiveness.  It is the heart of Model 0’s self‑tuning.
