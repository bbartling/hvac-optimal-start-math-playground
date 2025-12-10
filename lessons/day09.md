# Day 9 — The Dead‑Time Intercept (b)

**Goal:** Understand the overhead time in the quadratic model

## 1. Concept and Definitions

In Model 1 the intercept α₁,b accounts for fixed delays such as coil warm‑up,
valve stroking and sensor lag.  Even if ΔT were zero you still need a
few minutes to circulate water or air before any temperature change is
measurable.  The PNNL paper defines α₁,b as the minutes required to
change the indoor temperature by one degree【913477360246089†L448-L476】.
Choosing α₁,b appropriately prevents the model from predicting zero
runtime when ΔT is small.

## 2. How to Use It

Apply the concepts above using the formula or algorithm provided. Refer to the mini examples below for a demonstration.

## 3. Why This Matters

Understanding this concept allows you to build more accurate and efficient optimal‑start models, improving comfort and energy savings.

## 4. Mini‑Examples

Here's a simple Python demonstration:

```python
# Illustrate the impact of the intercept
alpha_a = 1.5
alpha_b = 5.0
for delta_t in [1, 4, 8]:
    t_pred = alpha_a * (delta_t ** 2) + alpha_b
    print(f'ΔT={delta_t}°F → time={t_pred:.1f} min')
```

## 5. Micro‑Exercises

1. Explain why the predicted time is never less than α₁,b.
2. How would you estimate α₁,b from historical data?
3. What building components contribute to dead‑time during warm‑up?
4. Create a simple Python file that performs the calculations from this lesson.
   Use only basic variables, arithmetic, print statements and at most a `for` loop over a list. Avoid defining functions or using `zip`.
   Hint: replicate the structure of the examples above but use your own numbers or dataset.

## 6. Key Takeaway

The intercept captures fixed delays in the system.  Without it, the model would unrealistically predict zero runtime for small temperature differences.
