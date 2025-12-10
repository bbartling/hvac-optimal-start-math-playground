# Day 23 — The Big Equation

**Goal:** Write down Model 3’s multiple regression formula

Model 3 predicts warm‑up time using three terms: (1) a coefficient α₃,a
for ΔT, (2) a coefficient α₃,b for ΔT×WF, and (3) a constant α₃,d.  The
PNNL paper expresses the model as t = α₃,a(ΔT) + α₃,b(ΔT·WF) + α₃,d
【913477360246089†L575-L590】.  This structure captures both the direct
effect of indoor temperature difference and the combined effect of indoor
and outdoor conditions.

## Python Mini‑Lesson

```python
# Compute Model 3 prediction with sample coefficients
delta_t = 5.0
WF = 0.8
alpha_a, alpha_b, alpha_d = 2.0, 1.5, 3.0
t_pred = alpha_a * delta_t + alpha_b * (delta_t * WF) + alpha_d
print(f'Predicted time = {t_pred:.1f} minutes')
```

## Exercises

1. Given α₃,a=1.8, α₃,b=2.2 and α₃,d=4.0, compute t for ΔT=6°F and WF=0.5.
2. Explain why adding the ΔT×WF term allows the model to react differently to cold versus mild weather.
3. Why is a constant term (α₃,d) needed even when ΔT=0?

## Key Takeaway

Model 3 combines multiple features to capture more complex dynamics.  It generalises Model 1 by including a weather interaction term.
