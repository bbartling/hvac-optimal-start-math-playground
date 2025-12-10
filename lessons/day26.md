# Day 26 — Handling Weird Coefficients

**Goal:** Deal with negative or nonsensical regression parameters

Regression can sometimes yield negative coefficients (e.g., α₃,b < 0),
suggesting that colder weather makes warm‑up faster.  Such results may
be caused by limited data or multicollinearity.  In practice you may
choose to clamp coefficients to zero or apply domain knowledge to
prevent nonsensical behaviour.  Always validate fitted models against
physical intuition.

## Python Mini‑Lesson

```python
# Example of clamping a negative coefficient
alpha_b = -0.5  # obtained from regression
if alpha_b < 0:
    alpha_b = 0.0
print(f'Clamped α₃,b = {alpha_b}')
```

## Exercises

1. Why might a regression algorithm produce a negative α₃,b?
2. Describe two strategies for handling unrealistic coefficients in practice.
3. How could you collect more data to reduce coefficient uncertainty?

## Key Takeaway

Regression coefficients must make physical sense.  Clamping or re‑estimating parameters helps avoid illogical predictions.
