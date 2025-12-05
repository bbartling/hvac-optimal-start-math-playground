# Day 34 — Coding Model 4 (First‑Order Response)

**Goal:** Write a reusable Python function to compute optimal start time using the logarithmic decay model.

## 1.  The Formula Revisited

Model 4 predicts warm‑up time using:

```
t = ln(alpha_a / DeltaT) / ln(alpha_c)
```

where:

* `alpha_a` is the acceptable error or deadband (e.g., 0.5°F).  
* `DeltaT` is the initial temperature difference.  
* `alpha_c` is the decay factor from Day 31.

## 2.  Python Implementation

```python
import math

def predict_model4(delta_t, alpha_a, alpha_c):
    """Predict warm‑up minutes using the first‑order model."""
    if delta_t <= 0:
        return 0.0
    # Avoid math domain errors by clamping values
    delta_t = max(delta_t, 1e-6)
    if alpha_c <= 0 or alpha_c >= 1:
        raise ValueError("alpha_c must be between 0 and 1")
    return math.log(alpha_a / delta_t) / math.log(alpha_c)

# Example usage
print(predict_model4(6.0, 0.5, 0.74))
```

You can incorporate smoothing on `alpha_c` as described previously to update your model with new data.

## 3.  Handling Edge Cases

* If `delta_t < alpha_a`, the numerator becomes `ln(alpha_a / delta_t)` which is positive — this yields a *negative* time, meaning you’re already within the deadband.  Clamp your result to zero.  
* If `alpha_c` is very close to 1, the denominator becomes small and the predicted time grows huge.  Limit `alpha_c` to a reasonable range (e.g., 0.5–0.95).

## 4.  Micro‑Exercises

1. Write unit tests for `predict_model4` that verify correct behaviour when `DeltaT` is below deadband, when `alpha_c` is out of bounds, and when typical values are used.  
2. Extend the function to accept a list of past `alpha_c` values and compute an EMA before prediction.  
3. Compare Model 4 predictions against real warm‑up data from your building.

## 5.  Key Takeaway

Implementing Model 4 requires careful handling of logarithms and edge cases, but it can give more realistic predictions for systems with exponential behaviour.
