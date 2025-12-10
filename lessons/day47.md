# Day 47 — Feature Engineering (Data Prep)

**Goal:** Prepare input data for gradient descent

Machine learning models are sensitive to the scale and format of input
features.  Scaling (normalising) ΔT values and encoding categorical
variables like "Monday" as 0/1 improves training.  A typical input
vector might be [scaled_ΔT, is_monday].  Scaling prevents large
numbers from dominating the gradient and helps weights learn at the
same pace【485764260655805†L152-L160】.

## Python Mini‑Lesson

```python
# Prepare features for a small dataset
delta_ts = [2, 5, 8]
is_monday = [0, 1, 0]
# Scale ΔT by dividing by the maximum
max_delta = max(delta_ts)
scaled_delta = [d / max_delta for d in delta_ts]
features = list(zip(scaled_delta, is_monday))
print('Features:', features)
```

## Exercises

1. Scale your own ΔT values and encode whether each day is Monday.
2. Why is one‑hot encoding necessary for categorical variables?
3. What might happen if you fail to scale features before training?

## Key Takeaway

Good feature engineering ensures that all inputs contribute appropriately during training.  Scaling and encoding are simple but powerful steps.
