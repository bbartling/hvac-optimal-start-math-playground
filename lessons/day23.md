# Day 23 — The Big Equation

**Goal:** Write down Model 3’s multiple regression formula

## 1. Concept and Definitions

Model 3 predicts warm‑up time using three terms: (1) a coefficient α₃,a
for ΔT, (2) a coefficient α₃,b for ΔT×WF, and (3) a constant α₃,d.  The
PNNL paper expresses the model as t = α₃,a(ΔT) + α₃,b(ΔT·WF) + α₃,d
【913477360246089†L575-L590】.  This structure captures both the direct
effect of indoor temperature difference and the combined effect of indoor
and outdoor conditions.

## 2. How to Use It

Apply the concepts above using the formula or algorithm provided. Refer to the mini examples below for a demonstration.

## 3. Why This Matters

Understanding this concept allows you to build more accurate and efficient optimal‑start models, improving comfort and energy savings.

## 4. Mini‑Examples

Here's a simple Python demonstration:

```python
# Compute Model 3 prediction with sample coefficients
delta_t = 5.0
WF = 0.8
alpha_a, alpha_b, alpha_d = 2.0, 1.5, 3.0
t_pred = alpha_a * delta_t + alpha_b * (delta_t * WF) + alpha_d
print(f'Predicted time = {t_pred:.1f} minutes')
```

## 5. Micro‑Exercises

1. Given α₃,a=1.8, α₃,b=2.2 and α₃,d=4.0, compute t for ΔT=6°F and WF=0.5.
2. Explain why adding the ΔT×WF term allows the model to react differently to cold versus mild weather.
3. Why is a constant term (α₃,d) needed even when ΔT=0?
4. Create a simple Python file that performs the calculations from this lesson.
   Use only basic variables, arithmetic, print statements and at most a `for` loop over a list. Avoid defining functions or using `zip`.
   Hint: replicate the structure of the examples above but use your own numbers or dataset.

## 6. Key Takeaway

Model 3 combines multiple features to capture more complex dynamics.  It generalises Model 1 by including a weather interaction term.
