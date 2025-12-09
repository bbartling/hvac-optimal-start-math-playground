# Day 44 — The Cost Function (MSE)

**Goal:** Learn how to mathematically quantify "how bad" a model is so the computer can fix it.

## 1. Defining "Wrongness"

To teach a computer, we need a single number that represents error. We can't just say "it looks off." We use the **Mean Squared Error (MSE)**.

$$
MSE = \frac{1}{n} \sum (\text{Actual} - \text{Predicted})^2
$$

## 2. Why Square the Error?

1.  **Removes Negatives:** An error of $-5$ minutes and $+5$ minutes are both equally bad. Squaring them makes both positive ($25$).
2.  **Punishes Big Mistakes:**
    * Being off by 2 minutes $\rightarrow$ Cost = 4.
    * Being off by 10 minutes $\rightarrow$ Cost = 100.
    * The model will fight much harder to fix a 10-minute error than a 2-minute error.

## 3. Micro‑Exercises

1.  Given three predictions: `[Predicted: 50, Actual: 60]`, `[Predicted: 40, Actual: 40]`, `[Predicted: 30, Actual: 25]`.
2.  Calculate the raw errors: `+10`, `0`, `-5`.
3.  Calculate the squares: `100`, `0`, `25`.
4.  Compute the average (MSE). This number is your "Cost."

## 4. Key Takeaway

The "Cost Function" is the scoreboard. The goal of the entire AI engine is simply to make this one number as small as possible.