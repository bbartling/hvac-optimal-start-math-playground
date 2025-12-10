# Day 29 — Thinking Like a Capacitor

**Goal:** Conceptualise buildings as thermal capacitors

## 1. Concept and Definitions

In electrical engineering a capacitor charges and discharges exponentially.
Buildings behave similarly: they warm quickly at first and then slow as
they approach set point.  This analogy leads to logarithmic models
where the time to reduce the error follows t ∝ ln(E0/E).  Recognising
this behaviour prepares you for Model 4.

## 2. How to Use It

Apply the concepts above using the formula or algorithm provided. Refer to the mini examples below for a demonstration.

## 3. Why This Matters

Understanding this concept allows you to build more accurate and efficient optimal‑start models, improving comfort and energy savings.

## 4. Mini‑Examples

Here's a simple Python demonstration:

```python
# Simulate exponential charging (analogous to heating)
import math
tau = 10.0  # time constant
time_values = [0, 5, 10, 20]
for t in time_values:
    fraction = 1 - math.exp(-t / tau)
    print(f't={t} min → fraction charged={fraction:.3f}')
```

## 5. Micro‑Exercises

1. What physical properties of a building correspond to a large time constant?
2. If the time constant is small, how does the system behave?
3. Give another real‑world system that follows exponential behaviour.
4. Create a simple Python file that performs the calculations from this lesson.
   Use only basic variables, arithmetic, print statements and at most a `for` loop over a list. Avoid defining functions or using `zip`.
   Hint: replicate the structure of the examples above but use your own numbers or dataset.

## 6. Key Takeaway

Thermal processes often mirror exponential charging and discharging.  This insight motivates the logarithmic formula in Model 4.
