# Day 48 — The Epoch Loop

**Goal:** Build the outer loop that repeats the learning process until the model is "smart."

## 1. What is an Epoch?

One **Epoch** means looking at the entire history dataset once, checking errors, and updating weights.
Real models need hundreds or thousands of epochs to converge on the perfect weights.

* **Epoch 1:** The model is guessing randomly. Error is huge.
* **Epoch 100:** The model has learned the general direction. Error is dropping.
* **Epoch 2,000:** The model has fine-tuned the decimal places. Error is minimal.

## 2. The Loop Structure

To make the AI learn, we wrap the update rule from Day 46 inside a loop.

```python
# The "Brain" Training Loop
for epoch in range(2000):
    
    # 1. Prediction (Forward Pass)
    guess = input * weight
    
    # 2. Error Calculation
    error = guess - actual
    
    # 3. Gradient Calculation (Backward Pass)
    gradient = error * input
    
    # 4. Weight Update (The Learning)
    weight = weight - (learning_rate * gradient)
```

## 3. Watching the Loss Drop

If your code is correct, the "Cost" (MSE) should decrease rapidly at first, then level off. This curve is called the **Learning Curve**.

  * If Loss goes UP: Your Learning Rate is too high (explosion).
  * If Loss doesn't move: Your Learning Rate is too low (stalled).

## 4. Micro‑Exercises

1.  Wrap your code from Day 46 in a loop that runs 100 times.
2.  Print the `weight` and `error` every 10 loops using `if epoch % 10 == 0:`.
3.  Watch the weight "walk" from its starting random guess toward the correct physical value.

## 5. Key Takeaway

Intelligence is just iteration. The computer isn't smart; it's just persistent.

