# Day 22 — The Missing Link: Weather Factor (WF)

**Goal:** Define the weather factor used in Model 3

## 1. Concept and Definitions

Model 3 introduces a weather factor (WF) to capture the combined effect
of indoor temperature difference and outdoor temperature.  A common
definition is WF = (T_sp − OAT) / 60, which scales the outdoor influence
to minutes.  Multiplying ΔT by WF yields a feature that grows when the
outdoor air is far from set point.  This additional feature allows
multiple regression to learn how weather amplifies or reduces warm‑up
time.

## 2. How to Use It

Apply the concepts above using the formula or algorithm provided. Refer to the mini examples below for a demonstration.

## 3. Why This Matters

Understanding this concept allows you to build more accurate and efficient optimal‑start models, improving comfort and energy savings.

## 4. Mini‑Examples

Here's a simple Python demonstration:

```python
# Compute the weather factor
T_sp = 70.0
oat = 30.0
WF = (T_sp - oat) / 60.0
delta_t = 8.0
feature = delta_t * WF
print(f'Weather factor WF = {WF:.2f}')
print(f'ΔT × WF        = {feature:.2f}')
```

## 5. Micro‑Exercises

1. Calculate WF for T_sp=75°F and OAT=50°F.
2. If WF is zero, what does that imply about the outdoor temperature?
3. Why do we divide by 60 in the definition of WF?
4. Create a simple Python file that performs the calculations from this lesson.
   Use only basic variables, arithmetic, print statements and at most a `for` loop over a list. Avoid defining functions or using `zip`.
   Hint: replicate the structure of the examples above but use your own numbers or dataset.

## 6. Key Takeaway

The weather factor combines indoor and outdoor information into a single number.  It forms one of the inputs for Model 3.
