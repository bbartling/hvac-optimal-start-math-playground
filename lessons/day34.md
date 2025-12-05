# Day 34 — Coding Model 4

**Goal:** Provide a concrete Python implementation of the logarithmic model with error checking.

## 1. Implementation

```python
import math

def predict_log(delta_t, deadband, decay):
    # Avoid divide-by-zero and negative logs
    if delta_t <= 0 or deadband <= 0 or decay <= 0 or decay >= 1:
        return 0
    numerator = math.log(deadband / delta_t)
    denominator = math.log(decay)
    return numerator / denominator

# Example usage
print(predict_log(8.0, 0.5, 0.74))
```

## 2. Error Handling

Notice the function checks that `decay` is between 0 and 1 (exclusive) and that the deadband and delta are positive.

## 3. Key Takeaway

A few lines of Python make Model 4 easy to implement.  Always add error checks when working with logs.
