# Day 7 — Week 1 Review: The Limits of Linear

**Goal:** Understand when the linear model breaks down

## 1. Concept and Definitions

Linear models assume a constant warm‑up rate, but buildings are complex.
On very cold mornings or deep setbacks the heat transfer slows down as
the zone approaches set point.  Linear models also ignore external
influences like outdoor temperature and thermal mass.  Use this review
to reflect on when Model 0 is adequate and when you need more advanced
models.

## 2. How to Use It

Apply the concepts above using the formula or algorithm provided. Refer to the mini examples below for a demonstration.

## 3. Why This Matters

Understanding this concept allows you to build more accurate and efficient optimal‑start models, improving comfort and energy savings.

## 4. Mini‑Examples

Here's a simple Python demonstration:

```python
# Compare linear predictions to actual times under different ΔT
rates = [0.20, 0.20]  # same rate assumed
deltas = [3, 8]      # small and large ΔT
actual_times = [16, 70]  # hypothetical observed times
for delta, rate, actual in zip(deltas, rates, actual_times):
    pred = delta / rate
    print(f'ΔT={delta}°F: predicted={pred:.1f} min, actual={actual} min')
```

## 5. Micro‑Exercises

1. For the example above, compute the percentage error for each case.
2. List two real‑world factors that violate the constant rate assumption.
3. How might adding outdoor temperature improve the prediction for large ΔT?
4. Create a simple Python file that performs the calculations from this lesson.
   Use only basic variables, arithmetic, print statements and at most a `for` loop over a list. Avoid defining functions or using `zip`.
   Hint: replicate the structure of the examples above but use your own numbers or dataset.

## 6. Key Takeaway

Model 0 works best for modest temperature differences and consistent conditions.  Extreme deltas or rapidly changing weather require nonlinear models.
