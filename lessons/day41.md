# Day 41 — Designing the Ultimate Hybrid

**Goal:** Create a decision tree combining multiple models and Monday logic.

## 1. Proposed Logic

```python
def ultimate_predict(delta_t, is_monday):
    if delta_t < 2:
        return model0_prediction(delta_t)
    elif not is_monday:
        return model3_prediction(delta_t)
    else:
        return model3_prediction(delta_t) + 60  # or multiply by factor
```

## 2. Discussion

* Small ΔT → Use simple linear EMA (Model 0).
* Normal weekday with ΔT > 2 °F → Use Model 3.
* Monday → Use Model 3 plus an adder or multiplier.

## 3. Key Takeaway

Combining models and heuristics yields robust performance across all conditions.
