# Day 34 — Coding Model 4

**Goal:** Implement the logarithmic formula safely

## 1. Concept and Definitions

Implementing Model 4 requires careful handling of logs.  You must avoid
taking the logarithm of zero or negative numbers.  Ensure ΔT > 0 and
decay_rate < 1.  If ΔT is within the deadband, you can return zero
runtime (already at set point).

## 2. How to Use It

Apply the concepts above using the formula or algorithm provided. Refer to the mini examples below for a demonstration.

## 3. Why This Matters

Understanding this concept allows you to build more accurate and efficient optimal‑start models, improving comfort and energy savings.

## 4. Mini‑Examples

Here's a simple Python demonstration:

```python
# Safe computation of Model 4
import math
delta_t, deadband, decay_rate = 5.0, 0.5, 0.8
if delta_t <= deadband:
    time = 0.0
else:
    # Ensure decay_rate is between 0 and 1
    time = math.log(deadband / delta_t) / math.log(decay_rate)
print(time)
```

## 5. Micro‑Exercises

1. Modify the function to handle heating and cooling modes separately with different deadbands.
2. What happens if you pass decay_rate=1?  Why is this invalid?
3. Integrate this function into a control loop that stops heating when t=0.
4. Create a simple Python file that performs the calculations from this lesson.
   Use only basic variables, arithmetic, print statements and at most a `for` loop over a list. Avoid defining functions or using `zip`.
   Hint: replicate the structure of the examples above but use your own numbers or dataset.

## 6. Key Takeaway

Robust code for Model 4 checks inputs and handles edge cases.  Careful implementation prevents mathematical errors.
