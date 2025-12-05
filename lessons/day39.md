# Day 39 — Experiment: The Weekend Factor

**Goal:** Explore multiplying model predictions by a constant to account for weekend cold soak.

## 1. Concept

Instead of adding a fixed hour, multiply the prediction by a **cold soak factor** (e.g., 1.2–1.3).  This scales the prediction relative to ΔT.

## 2. Example

If Model 3 predicts 45 min and the factor is 1.25, the adjusted time is 56.25 min.

## 3. Python

```python
def apply_weekend_factor(t_pred, factor=1.25):
    return t_pred * factor
```

## 4. Key Takeaway

Multipliers provide a flexible way to adjust for Mondays.  Tune the factor to your building.
