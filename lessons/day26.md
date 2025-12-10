# Day 26 — Handling Weird Coefficients

**Goal:** Deal with negative or nonsensical regression parameters

## 1. Concept and Definitions

Regression can sometimes yield negative coefficients (e.g., α₃,b < 0),
suggesting that colder weather makes warm‑up faster.  Such results may
be caused by limited data or multicollinearity.  In practice you may
choose to clamp coefficients to zero or apply domain knowledge to
prevent nonsensical behaviour.  Always validate fitted models against
physical intuition.

## 2. How to Use It

Apply the concepts above using the formula or algorithm provided. Refer to the mini examples below for a demonstration.

## 3. Why This Matters

Understanding this concept allows you to build more accurate and efficient optimal‑start models, improving comfort and energy savings.

## 4. Mini‑Examples

Here's a simple Python demonstration:

```python
# Example of clamping a negative coefficient
alpha_b = -0.5  # obtained from regression
if alpha_b < 0:
    alpha_b = 0.0
print(f'Clamped α₃,b = {alpha_b}')
```

## 5. Micro‑Exercises

1. Why might a regression algorithm produce a negative α₃,b?
2. Describe two strategies for handling unrealistic coefficients in practice.
3. How could you collect more data to reduce coefficient uncertainty?
4. Create a simple Python file that performs the calculations from this lesson.
   Use only basic variables, arithmetic, print statements and at most a `for` loop over a list. Avoid defining functions or using `zip`.
   Hint: replicate the structure of the examples above but use your own numbers or dataset.

## 6. Key Takeaway

Regression coefficients must make physical sense.  Clamping or re‑estimating parameters helps avoid illogical predictions.
