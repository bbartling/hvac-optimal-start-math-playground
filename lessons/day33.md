# Day 33 — Comparing Logarithmic vs Quadratic Models

**Goal:** Contrast Model 4 (logarithmic decay) with Model 1 (quadratic) and show how to choose between them.

## 1.  Conceptual Differences

* **Model 1** fits a quadratic curve of the form `t = a*(DeltaT)**2 + b`.  It assumes the warm‑up gets *harder* as ΔT increases — each extra degree costs more time.  
* **Model 4** assumes the error decays exponentially, leading to a logarithmic formula for time: `t = ln(alpha_a / DeltaT) / ln(alpha_c)`.  It implies the system heats quickly at first but slows as it approaches setpoint.

## 2.  Choosing a Model

* Use **Model 1** when the system has high thermal mass and the heating power stays constant.  
* Use **Model 4** when the system output throttles down naturally (e.g., variable‑speed compressors) or when sensors show a clear exponential approach to setpoint.

## 3.  Quick Comparison with Python

The following script computes predicted warm‑up times from both models for a range of ΔT values:

```python
import math

# Quadratic coefficients (example)
a_quad = 0.6
b_quad = 8.0
# Logarithmic coefficients
alpha_a = 0.5  # deadband
alpha_c = 0.75  # decay factor

def model1_time(delta_t):
    return a_quad * (delta_t**2) + b_quad

def model4_time(delta_t):
    if delta_t <= 0:
        return 0
    return math.log(alpha_a / delta_t) / math.log(alpha_c)

for dt in [2, 4, 6, 8, 10]:
    print(f"ΔT={dt}: M1={model1_time(dt):.1f} min, M4={model4_time(dt):.1f} min")
```

When ΔT is small, both models may predict similar times.  For large ΔT, Model 1 can blow up (quadratic growth), whereas Model 4 plateaus more gently.

## 4.  Micro‑Exercises

1. Plug in your own coefficients for Model 1 and Model 4 from real building data.  Compare the predictions for ΔT = 2–10°F.  
2. Create a simple bar chart (using `matplotlib`) to visualise the differences.  
3. Discuss in 2–3 sentences which model better represents the warm‑up behaviour at your site.

## 5.  Key Takeaway

Quadratic and logarithmic models capture different physics.  Comparing them helps you decide which assumptions match your equipment.
