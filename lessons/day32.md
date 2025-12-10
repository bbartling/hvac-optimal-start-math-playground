# Day 32 — The Coast‑to‑Stop Effect

**Goal:** Explain why heating slows as set point nears

## 1. Concept and Definitions

As the zone temperature approaches the set point, the driving force for
heat transfer diminishes.  The coil may also modulate or cycle off
to prevent overshoot.  This leads to the ‘coast‑to‑stop’ effect
captured by Model 4.  The logarithmic formula accounts for this
slowing by predicting longer times near the end of the warm‑up.

## 2. How to Use It

Apply the concepts above using the formula or algorithm provided. Refer to the mini examples below for a demonstration.

## 3. Why This Matters

Understanding this concept allows you to build more accurate and efficient optimal‑start models, improving comfort and energy savings.

## 4. Mini‑Examples

Here's a simple Python demonstration:

```python
# Simulate temperature approach using a simple decay model
T_sp = 70.0
T = 60.0
alpha_c = 0.85
for minute in range(1, 11):
    error = T_sp - T
    T += error * (1 - alpha_c)  # fractional approach
    print(f'min {minute}: T={T:.2f}°F, error={T_sp - T:.2f}°F')
```

## 5. Micro‑Exercises

1. What would happen if the coil delivered constant power until set point?
2. Describe two physical reasons why heating slows near set point.
3. How does Model 4 prevent overshooting the target temperature?
4. Create a simple Python file that performs the calculations from this lesson.
   Use only basic variables, arithmetic, print statements and at most a `for` loop over a list. Avoid defining functions or using `zip`.
   Hint: replicate the structure of the examples above but use your own numbers or dataset.

## 6. Key Takeaway

The coast‑to‑stop behaviour reflects reduced temperature difference and modulation near set point.  Model 4’s logarithmic form captures this effect.
