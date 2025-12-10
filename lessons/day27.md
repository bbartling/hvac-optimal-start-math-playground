# Day 27 — Tuning Model 3

**Goal:** Select history length and prevent overfitting

Model 3 requires enough data to reliably estimate three parameters. 
Using too little history can overfit noise; using too much may make the
model slow to adapt.  PNNL recommends using around ten days of data
for coefficient updates.  You can also apply an EMA to the coefficients
similar to Model 1 to gradually adjust α₃,a, α₃,b and α₃,d.

## Python Mini‑Lesson

```python
# Simple coefficient update with EMA
alpha = 0.1
coeff_old = {'a': 1.5, 'b': 0.8, 'd': 2.0}
coeff_new = {'a': 1.6, 'b': 1.0, 'd': 1.8}
for key in coeff_old:
    coeff_old[key] = coeff_old[key] + alpha * (coeff_new[key] - coeff_old[key])
print('Updated coefficients:', coeff_old)
```

## Exercises

1. What happens if you update coefficients after every single day versus every 10 days?
2. Suggest a method to detect overfitting in Model 3.
3. Could you assign different α values to α₃,a, α₃,b and α₃,d?  Why or why not?

## Key Takeaway

Balancing the amount of history and the speed of adaptation prevents overfitting and keeps Model 3 responsive to real trends.
