# Day 20 — Sensitivity Check

**Goal:** Explore how changes in outdoor temperature impact the ratio

## 1. Concept and Definitions

The weather ratio magnifies or reduces the predicted time depending on
how much colder or warmer today is relative to yesterday.  A sensitivity
check evaluates how big the effect is.  For example, a 10 °F colder day
might lengthen the runtime by 20 %, while a 10 °F warmer day might
shorten it.  Understanding this sensitivity helps set realistic limits on
the model’s output.

## 2. How to Use It

Apply the concepts above using the formula or algorithm provided. Refer to the mini examples below for a demonstration.

## 3. Why This Matters

Understanding this concept allows you to build more accurate and efficient optimal‑start models, improving comfort and energy savings.

## 4. Mini‑Examples

Here's a simple Python demonstration:

```python
# Evaluate ratio sensitivity for heating mode
T_ref = 32.0
oat_prev = 25.0
for oat_curr in [15.0, 20.0, 25.0, 30.0]:
    ratio = (T_ref - oat_prev) / (T_ref - oat_curr)
    print(f'Today OAT={oat_curr}°F → Ratio={ratio:.2f}')
```

## 5. Micro‑Exercises

1. Plot the ratio as a function of today’s OAT for fixed oat_prev and T_ref.
2. At what temperature difference does the ratio become extremely large?
3. How could you modify Model 2 to cap the ratio when the difference is extreme?
4. Create a simple Python file that performs the calculations from this lesson.
   Use only basic variables, arithmetic, print statements and at most a `for` loop over a list. Avoid defining functions or using `zip`.
   Hint: replicate the structure of the examples above but use your own numbers or dataset.

## 6. Key Takeaway

Sensitivity checks reveal how weather swings translate into runtime changes.  They also expose cases where the ratio might need clamping.
