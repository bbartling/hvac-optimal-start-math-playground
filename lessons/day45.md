# Day 45 — The Gradient (The Nudge)

**Goal:** Compute gradients to update weights

## 1. Concept and Definitions

The gradient of the cost function tells us how to adjust each weight to
reduce error.  For a simple linear model y = w·x, the gradient of the
MSE with respect to w is proportional to Σ (prediction − actual) × x.
We then update w ← w − η × gradient, where η is the learning rate【485764260655805†L152-L160】.

## 2. How to Use It

Apply the concepts above using the formula or algorithm provided. Refer to the mini examples below for a demonstration.

## 3. Why This Matters

Understanding this concept allows you to build more accurate and efficient optimal‑start models, improving comfort and energy savings.

## 4. Mini‑Examples

Here's a simple Python demonstration:

```python
# Perform one gradient descent step for a single weight
x_data = [1, 2, 3]
y_actual = [2, 4, 6]
w = 0.0  # initial weight
learning_rate = 0.1
# Compute gradient of MSE w.r.t w
grad = sum((w * x - y) * x for x, y in zip(x_data, y_actual)) * 2 / len(x_data)
w = w - learning_rate * grad
print(f'Updated weight w={w:.2f}')
```

## 5. Micro‑Exercises

1. Repeat the update step 10 times and observe how w approaches the true value.
2. What happens if the learning rate η is too large?
3. Derive the gradient formula for a model with two weights.
4. Create a simple Python file that performs the calculations from this lesson.
   Use only basic variables, arithmetic, print statements and at most a `for` loop over a list. Avoid defining functions or using `zip`.
   Hint: replicate the structure of the examples above but use your own numbers or dataset.

## 6. Key Takeaway

Gradients point in the direction of steepest error increase.  Updating weights opposite to the gradient reduces error over time.
