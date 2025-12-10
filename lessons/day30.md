# Day 30 — The Logarithm (ln)

**Goal:** Use natural logarithms to compute time in Model 4

## 1. Concept and Definitions

Model 4 predicts the time to reach set point using a logarithmic decay
formula:

    t = ln(Deadband/ΔT) / ln(DecayRate)

where Deadband is an acceptable error band (e.g., 0.5 °F), ΔT is the
current temperature difference, and DecayRate (α₄,c) describes how
quickly the error shrinks from one minute to the next.  As ΔT gets small
the numerator ln(Deadband/ΔT) grows, lengthening the predicted time.

## 2. How to Use It

Apply the concepts above using the formula or algorithm provided. Refer to the mini examples below for a demonstration.

## 3. Why This Matters

Understanding this concept allows you to build more accurate and efficient optimal‑start models, improving comfort and energy savings.

## 4. Mini‑Examples

Here's a simple Python demonstration:

```python
# Compute Model 4 prediction
import math
deadband = 0.5
delta_t = 4.0
decay_rate = 0.8
t_pred = math.log(deadband / delta_t) / math.log(decay_rate)
print(f'Predicted time = {t_pred:.1f} minutes')
```

## 5. Micro‑Exercises

1. Using decay_rate=0.85 and Deadband=0.5°F, compute t for ΔT=6°F.
2. Why does the time grow large as ΔT approaches the deadband?
3. Explain what happens if decay_rate≥1.
4. Create a simple Python file that performs the calculations from this lesson.
   Use only basic variables, arithmetic, print statements and at most a `for` loop over a list. Avoid defining functions or using `zip`.
   Hint: replicate the structure of the examples above but use your own numbers or dataset.

## 6. Key Takeaway

The logarithmic formula captures slowing heat transfer as the zone approaches set point.  It differs fundamentally from linear or quadratic models.
