# Day 31 — Calculating the Decay Rate (α₄,c)

**Goal:** Estimate how quickly the error shrinks from logged data

## 1. Concept and Definitions

Model 4 requires a decay rate α₄,c between 0 and 1.  One way to
estimate it is to examine how the error (T_sp − T_z) changes minute
over minute.  If e_t and e_{t−1} are consecutive errors, the ratio
e_t/e_{t−1} approximates α₄,c.  Averaging these ratios over a warm‑up
gives a good estimate.

## 2. How to Use It

Apply the concepts above using the formula or algorithm provided. Refer to the mini examples below for a demonstration.

## 3. Why This Matters

Understanding this concept allows you to build more accurate and efficient optimal‑start models, improving comfort and energy savings.

## 4. Mini‑Examples

Here's a simple Python demonstration:

```python
# Estimate decay rate from error measurements
errors = [8.0, 6.5, 5.0, 3.8, 3.0]  # ΔT values at successive minutes
ratios = [errors[i] / errors[i-1] for i in range(1, len(errors))]
alpha_c = sum(ratios) / len(ratios)
print(f'Estimated decay rate α₄,c = {alpha_c:.2f}')
```

## 5. Micro‑Exercises

1. Record ΔT every minute during a warm‑up and compute α₄,c.
2. What does α₄,c≈1 imply about the system?
3. Why must α₄,c be less than 1 for heating/cooling?
4. Create a simple Python file that performs the calculations from this lesson.
   Use only basic variables, arithmetic, print statements and at most a `for` loop over a list. Avoid defining functions or using `zip`.
   Hint: replicate the structure of the examples above but use your own numbers or dataset.

## 6. Key Takeaway

By averaging successive error ratios you can estimate the decay rate used in Model 4.  It quantifies how quickly the system approaches set point.
