# Day 11 — Simple Regression (Line Fitting)

**Goal:** Fit a straight line through noisy data without statistics

## 1. Concept and Definitions

Regression finds the line that minimises the squared vertical distance
between your data points and the model.  For a simple linear relationship
(y = α + βx), the ordinary least squares solution has closed‑form
expressions for the intercept and slope.  Wikipedia gives the formulas
for α̂ and β̂ in terms of sums of x and y【722350863221826†L331-L338】.
You can implement these formulas directly in Python to fit Model 0 or
Model 1 on historical data.

## 2. How to Use It

Apply the concepts above using the formula or algorithm provided. Refer to the mini examples below for a demonstration.

## 3. Why This Matters

Understanding this concept allows you to build more accurate and efficient optimal‑start models, improving comfort and energy savings.

## 4. Mini‑Examples

Here's a simple Python demonstration:

```python
# Fit a line to (x, y) data using the closed‑form OLS solution
xs = [1, 3, 5, 7]
ys = [10, 18, 27, 40]
n = len(xs)
sum_x = sum(xs)
sum_y = sum(ys)
sum_xy = sum(x * y for x, y in zip(xs, ys))
sum_x2 = sum(x * x for x in xs)

# Compute slope β and intercept α
beta = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
alpha = (sum_y - beta * sum_x) / n

print(f'Fitted line: y = {alpha:.2f} + {beta:.2f} x')
```

## 5. Micro‑Exercises

1. Use the code above to fit a line through the points (2,15), (4,22) and (6,32).
2. Explain why minimising squared error is preferred over minimising absolute error.
3. How would adding more noisy points affect the fitted slope and intercept?
4. Create a simple Python file that performs the calculations from this lesson.
   Use only basic variables, arithmetic, print statements and at most a `for` loop over a list. Avoid defining functions or using `zip`.
   Hint: replicate the structure of the examples above but use your own numbers or dataset.

## 6. Key Takeaway

Closed‑form regression formulas let you compute slope and intercept without any external libraries.  This is the foundation of self‑tuning models.
