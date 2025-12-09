# Day 45 — The Gradient (The "Nudge")

**Goal:** Understand the logic of **Gradient Descent**—how the computer knows which direction to change the weights.

## 1. The Mountain in the Fog

Imagine you are standing on a mountain (the Cost Function) in total fog. You want to get to the bottom (Zero Error). You can't see the bottom, but you can feel the slope under your feet.

* If the slope goes **up** to the right, you step **left**.
* If the slope goes **down** to the right, you step **right**.

## 2. The Derivative (Slope)

In our simple prediction $y = w \cdot x$:
* If we guess too high, the "slope" of the error is positive. We must **decrease** $w$.
* If we guess too low, the "slope" is negative. We must **increase** $w$.

The formula for this slope (Gradient) with respect to the weight is:

$$
\text{Gradient} = \text{Error} \times \text{Input}
$$

## 3. Micro‑Exercises

1.  Scenario: Input $\Delta T = 10$. Actual = 60.
2.  Current Weight guess = 8. Prediction = $8 \times 10 = 80$.
3.  Error = $80 - 60 = +20$ (Too High).
4.  Gradient = $20 \times 10 = 200$.
5.  Since the gradient is positive, we must subtract from our weight. New weight might be 7.9.

## 4. Key Takeaway

The "Gradient" tells the model two things: which direction to move (sign), and how big a step to take (magnitude).