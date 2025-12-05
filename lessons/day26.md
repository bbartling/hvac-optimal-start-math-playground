# Day 26 — Implement Self‑Tuning Update Logic

**Goal:** Focus on the code that updates model coefficients after each warm‑up.

Self‑tuning requires careful handling of new observations.  You need to compute new coefficients, blend them, and handle edge cases gracefully.

## 1.  Update Logic for Model 0

```python
def update_rate_ema(deltaT, actual_minutes, rate_ema, alpha):
    # Avoid division by zero
    if actual_minutes <= 0 or deltaT <= 0:
        return rate_ema
    observed_rate = deltaT / actual_minutes
    return rate_ema + alpha * (observed_rate - rate_ema)
```

## 2.  Update Logic for Model 1

```python
def update_coefficients_model1(deltaT, actual_minutes, a_old, b_old, alpha):
    # Update a using a temporary slope from one point
    if deltaT <= 0:
        return a_old, b_old
    x = deltaT ** 2
    a_today = actual_minutes / x
    a_new = (1 - alpha) * a_old + alpha * a_today
    # Optionally update b only when you have at least two points
    return a_new, b_old
```

## 3.  Update Logic for Model 3

For a single morning you can estimate `a_today` while keeping `b` and `d` constant.  After three mornings you can solve the full 3×3 system and then blend all coefficients.

```python
def update_coefficients_model3(deltaT, wf, actual_minutes, a_old, b_old, d_old, alpha):
    x1 = deltaT
    x2 = deltaT * wf
    if x1 <= 0:
        return a_old, b_old, d_old
    # Approximate a_today assuming b and d fixed for one point
    a_today = (actual_minutes - d_old) / x1 - b_old * wf
    a_new = (1 - alpha) * a_old + alpha * a_today
    return a_new, b_old, d_old
```

For the full update after three datapoints, solve the 3×3 system as in Day 19 then blend each coefficient.

## Mini‑Exercises

1. Modify the Model 1 update function so that `b` is updated when you provide two warm‑up datapoints at once.
2. Write a function that, given a list of the last three Model 3 datapoints, solves for `a`, `b` and `d` and blends them into the old coefficients.
3. Implement a check that skips updating when `DeltaT` is below a small threshold (e.g. 1 °F) to avoid noisy learning.

## Key Takeaway

Updating the model is where the learning happens.  Blend new observations carefully, handle edge cases (zero runtime or zero ΔT), and choose your smoothing factor wisely.  Good update logic turns raw datapoints into reliable coefficients.