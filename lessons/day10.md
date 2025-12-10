# Day 10 — The Slope Coefficient (a)

**Goal:** Relate the quadratic coefficient to thermal mass

## 1. Concept and Definitions

The coefficient α₁,a determines how quickly time grows with (ΔT)².
Higher values correspond to heavier or poorly insulated buildings that
warm slowly; lower values represent lightweight, responsive zones.  In the
PNNL model, α₁,a is computed from previous days’ data【913477360246089†L448-L476】.
By tuning α₁,a you can make the model fit the observed warm‑up behaviour.

## 2. How to Use It

Apply the concepts above using the formula or algorithm provided. Refer to the mini examples below for a demonstration.

## 3. Why This Matters

Understanding this concept allows you to build more accurate and efficient optimal‑start models, improving comfort and energy savings.

## 4. Mini‑Examples

Here's a simple Python demonstration:

```python
# Visualise how α₁,a affects warm‑up time
delta_t = 5.0
for alpha_a in [0.5, 1.0, 2.0]:
    alpha_b = 2.0
    t_pred = alpha_a * (delta_t ** 2) + alpha_b
    print(f'α₁,a={alpha_a} → predicted={t_pred:.1f} min')
```

## 5. Micro‑Exercises

1. If α₁,a increases, what happens to the predicted time for the same ΔT?
2. Why might an exterior zone have a larger α₁,a than an interior zone?
3. How could you experimentally determine α₁,a for a particular building?
4. Create a simple Python file that performs the calculations from this lesson.
   Use only basic variables, arithmetic, print statements and at most a `for` loop over a list. Avoid defining functions or using `zip`.
   Hint: replicate the structure of the examples above but use your own numbers or dataset.

## 6. Key Takeaway

The slope coefficient reflects the building’s thermal mass.  Larger values slow the warm‑up and lengthen the predicted runtime.
