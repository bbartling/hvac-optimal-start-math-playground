# Day 14 — Week 2 Review: Model 0 vs. Model 1

**Goal:** Compare linear and quadratic predictions for typical scenarios

## 1. Concept and Definitions

Model 0 predicts time as t = ΔT / rate; Model 1 uses t = α₁,a·(ΔT)² + α₁,b.
For small temperature differences the two models often agree, but for
large ΔT the quadratic term dominates.  Use this review to compare
predictions on the same dataset and decide which model is more
appropriate.

## 2. How to Use It

Apply the concepts above using the formula or algorithm provided. Refer to the mini examples below for a demonstration.

## 3. Why This Matters

Understanding this concept allows you to build more accurate and efficient optimal‑start models, improving comfort and energy savings.

## 4. Mini‑Examples

Here's a simple Python demonstration:

```python
# Compare Model 0 and Model 1 predictions
delta_ts = [2, 5, 8]
rate = 0.20
alpha_a, alpha_b = 1.2, 3.0
for delta in delta_ts:
    t0 = delta / rate
    t1 = alpha_a * (delta ** 2) + alpha_b
    print(f'ΔT={delta}°F → Model0={t0:.1f} min, Model1={t1:.1f} min')
```

## 5. Micro‑Exercises

1. At what ΔT do the two models begin to diverge significantly?
2. Which model would you trust for an interior zone with small setbacks?
3. Suggest a hybrid approach for zones that occasionally experience large ΔT.
4. Create a simple Python file that performs the calculations from this lesson.
   Use only basic variables, arithmetic, print statements and at most a `for` loop over a list. Avoid defining functions or using `zip`.
   Hint: replicate the structure of the examples above but use your own numbers or dataset.

## 6. Key Takeaway

Linear and quadratic models can both be useful.  The best choice depends on the magnitude of ΔT and the thermal characteristics of the zone.
