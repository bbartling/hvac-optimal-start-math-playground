# Day 47 — Feature Engineering (Data Prep)

**Goal:** Prepare input data for gradient descent

## 1. Concept and Definitions

Machine learning models are sensitive to the scale and format of input
features.  Scaling (normalising) ΔT values and encoding categorical
variables like "Monday" as 0/1 improves training.  A typical input
vector might be [scaled_ΔT, is_monday].  Scaling prevents large
numbers from dominating the gradient and helps weights learn at the
same pace【485764260655805†L152-L160】.

## 2. How to Use It

Apply the concepts above using the formula or algorithm provided. Refer to the mini examples below for a demonstration.

## 3. Why This Matters

Understanding this concept allows you to build more accurate and efficient optimal‑start models, improving comfort and energy savings.

## 4. Mini‑Examples

Here's a simple Python demonstration:

```python
# Prepare features for a small dataset
delta_ts = [2, 5, 8]
is_monday = [0, 1, 0]
# Scale ΔT by dividing by the maximum
max_delta = max(delta_ts)
scaled_delta = [d / max_delta for d in delta_ts]
features = list(zip(scaled_delta, is_monday))
print('Features:', features)
```

## 5. Micro‑Exercises

1. Scale your own ΔT values and encode whether each day is Monday.
2. Why is one‑hot encoding necessary for categorical variables?
3. What might happen if you fail to scale features before training?
4. Create a simple Python file that performs the calculations from this lesson.
   Use only basic variables, arithmetic, print statements and at most a `for` loop over a list. Avoid defining functions or using `zip`.
   Hint: replicate the structure of the examples above but use your own numbers or dataset.

## 6. Key Takeaway

Good feature engineering ensures that all inputs contribute appropriately during training.  Scaling and encoding are simple but powerful steps.
