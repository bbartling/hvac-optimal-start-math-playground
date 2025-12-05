# Day 23 — Implement Model 0, 1 and 3 in Basic Python

**Goal:** Write simple scripts that embody the equations and updates you’ve learned, using only Python’s built‑in operators.

This lesson isn’t about production‑ready code — it’s about translating formulas into runnable scripts so you can experiment and build intuition.

## 1.  Model 0 Implementation

```python
# Initial guess and smoothing factor
rate_ema = 0.20  # degrees per minute
alpha = 0.1

def predict_model0(deltaT, rate):
    return deltaT / rate

def update_model0(deltaT, actual_minutes, rate, alpha):
    if actual_minutes <= 0:
        return rate
    observed_rate = deltaT / actual_minutes
    return rate + alpha * (observed_rate - rate)

# Example usage
deltaT = 6
minutes_predicted = predict_model0(deltaT, rate_ema)
minutes_actual = 30
rate_ema = update_model0(deltaT, minutes_actual, rate_ema, alpha)
```

## 2.  Model 1 Implementation

```python
# Coefficients and smoothing factor
a = 0.8
b = 8
alpha = 0.2

def predict_model1(deltaT, a, b):
    return a * (deltaT ** 2) + b

def update_model1(deltaT, actual_minutes, a, b, alpha):
    # Compute a temporary slope from a single point
    if deltaT <= 0:
        return a, b
    x = deltaT ** 2
    a_today = actual_minutes / x
    a_new = (1 - alpha) * a + alpha * a_today
    # b can be updated only if you have more than one point; keep it for now
    return a_new, b

# Example usage
deltaT = 5
minutes_predicted = predict_model1(deltaT, a, b)
minutes_actual = 26
a, b = update_model1(deltaT, minutes_actual, a, b, alpha)
```

## 3.  Model 3 Implementation

```python
# Coefficients and smoothing factor
a = 3.0
b = 6.0
d = 2.0
alpha = 0.15

def weather_factor(oat, oat_ref=65, oat_min=0):
    return max(0.0, min(1.0, (oat_ref - oat) / (oat_ref - oat_min)))

def predict_model3(deltaT, wf, a, b, d):
    return a * deltaT + b * (deltaT * wf) + d

def update_model3(deltaT, wf, actual_minutes, a, b, d, alpha):
    # For a single point, derive temporary coefficients assuming b and d constant
    x1 = deltaT
    x2 = deltaT * wf
    if x1 == 0:
        return a, b, d
    # Solve for a_today assuming d stays the same
    # a_today = (actual_minutes - d) / x1 - (b * x2 / x1)  # simplified case
    a_today = (actual_minutes - d) / x1 - b * wf  # simplified
    a_new = (1 - alpha) * a + alpha * a_today
    return a_new, b, d

# Example usage
deltaT = 7
wf = weather_factor(oat=30)
minutes_predicted = predict_model3(deltaT, wf, a, b, d)
minutes_actual = 60
a, b, d = update_model3(deltaT, wf, minutes_actual, a, b, d, alpha)
```

## Mini‑Exercises

1. Run the Model 0 script with a series of warm‑up events to see how `rate_ema` changes over time.  Does it stabilise?
2. Modify the Model 1 update function to also update `b` when you provide two points at once.
3. Extend the Model 3 update function to solve for all three coefficients when you accumulate three datapoints.

## Key Takeaway

Implementing the models yourself helps solidify the math.  Even with just lists and loops, you can simulate warm‑up mornings, update coefficients and see how predictions evolve.