# Day 7 — Week 1 Review: The Limits of Linear

**Goal:** Understand when the linear model breaks down

Linear models assume a constant warm‑up rate, but buildings are complex.
On very cold mornings or deep setbacks the heat transfer slows down as
the zone approaches set point.  Linear models also ignore external
influences like outdoor temperature and thermal mass.  Use this review
to reflect on when Model 0 is adequate and when you need more advanced
models.

## Python Mini‑Lesson

```python
# Compare linear predictions to actual times under different ΔT
rates = [0.20, 0.20]  # same rate assumed
deltas = [3, 8]      # small and large ΔT
actual_times = [16, 70]  # hypothetical observed times
for delta, rate, actual in zip(deltas, rates, actual_times):
    pred = delta / rate
    print(f'ΔT={delta}°F: predicted={pred:.1f} min, actual={actual} min')
```

## Exercises

1. For the example above, compute the percentage error for each case.
2. List two real‑world factors that violate the constant rate assumption.
3. How might adding outdoor temperature improve the prediction for large ΔT?

## Key Takeaway

Model 0 works best for modest temperature differences and consistent conditions.  Extreme deltas or rapidly changing weather require nonlinear models.
