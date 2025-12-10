# Day 8 — Why Heat Transfer isn’t Linear

**Goal:** Recognise that warm‑up time grows faster than ΔT

## 1. Concept and Definitions

In many buildings the last few degrees take longer than the first.  This
non‑linear behaviour occurs because heat transfer slows as the zone
approaches set point; the walls, furniture and air must all warm up.
PNNL’s Model 1 captures this by squaring the temperature difference:
t = α₁,a × (ΔT)² + α₁,b 【913477360246089†L448-L476】.  The square term
makes the runtime grow rapidly with large ΔT, better matching reality.

## 2. How to Use It

Apply the concepts above using the formula or algorithm provided. Refer to the mini examples below for a demonstration.

## 3. Why This Matters

Understanding this concept allows you to build more accurate and efficient optimal‑start models, improving comfort and energy savings.

## 4. Mini‑Examples

Here's a simple Python demonstration:

```python
# Compute warm‑up time using a quadratic model
delta_t = 6.0
alpha_a = 1.5  # minutes per (degree)^2
alpha_b = 2.5  # minutes
t_pred = alpha_a * (delta_t ** 2) + alpha_b
print(f'Predicted time = {t_pred:.1f} minutes')
```

## 5. Micro‑Exercises

1. Using α₁,a=1.0 and α₁,b=3.0, compute predicted times for ΔT=4 °F and ΔT=8 °F.
2. Explain why squaring ΔT exaggerates large temperature differences.
3. Give an example of a high‑mass zone where Model 1 would outperform Model 0.
4. Create a simple Python file that performs the calculations from this lesson.
   Use only basic variables, arithmetic, print statements and at most a `for` loop over a list. Avoid defining functions or using `zip`.
   Hint: replicate the structure of the examples above but use your own numbers or dataset.

## 6. Key Takeaway

Quadratic models reflect the slowing heat transfer near set point.  The (ΔT)² term makes large setbacks require disproportionately longer preheat times.
