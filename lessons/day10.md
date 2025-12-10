# Day 10 — The Slope Coefficient (a)

**Goal:** Relate the quadratic coefficient to thermal mass

The coefficient α₁,a determines how quickly time grows with (ΔT)².
Higher values correspond to heavier or poorly insulated buildings that
warm slowly; lower values represent lightweight, responsive zones.  In the
PNNL model, α₁,a is computed from previous days’ data【913477360246089†L448-L476】.
By tuning α₁,a you can make the model fit the observed warm‑up behaviour.

## Python Mini‑Lesson

```python
# Visualise how α₁,a affects warm‑up time
delta_t = 5.0
for alpha_a in [0.5, 1.0, 2.0]:
    alpha_b = 2.0
    t_pred = alpha_a * (delta_t ** 2) + alpha_b
    print(f'α₁,a={alpha_a} → predicted={t_pred:.1f} min')
```

## Exercises

1. If α₁,a increases, what happens to the predicted time for the same ΔT?
2. Why might an exterior zone have a larger α₁,a than an interior zone?
3. How could you experimentally determine α₁,a for a particular building?

## Key Takeaway

The slope coefficient reflects the building’s thermal mass.  Larger values slow the warm‑up and lengthen the predicted runtime.
