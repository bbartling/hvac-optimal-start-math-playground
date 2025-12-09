# Day 43 — Algebra vs. Iteration

**Goal:** Understand the fundamental difference between "solving" an equation (Model 3) and "learning" an equation (Machine Learning).

## 1. The Closed Form vs. The Learning Loop

Up until now (Models 0–3), we used algebra to find the exact answer immediately. For Model 3, we used matrix inversion to snap directly to the best coefficients.

**Machine Learning (ML)** works differently. It doesn't know the algebra formula to solve the problem. Instead, it plays a game of "Hot or Cold":
1.  Make a random guess.
2.  Check how wrong the guess is.
3.  Nudge the numbers slightly to be less wrong.
4.  Repeat 1,000 times.

## 2. Why bother?

If Algebra is faster, why use ML?
* **Flexibility:** Algebra requires a rigid formula shape. ML can adapt to shapes we haven't defined yet.
* **The Monday Problem:** We can feed "Monday" into the engine as a raw input and let the math figure out the penalty, rather than coding `IF Monday THEN +60`.

## 3. Micro‑Exercises

1.  Take a simple equation: $y = 2x$. Pretend you don't know the "2".
2.  Guess that $y = 5x$. Test with $x=10$. (Target=20, Guess=50).
3.  You are too high. Lower your guess to $y=3x$. Test again.
4.  This process of manually adjusting your guess based on the error is exactly what the Python code will do.

## 4. Key Takeaway

Traditional control logic "calculates" the answer. AI "searches" for the answer by making mistakes and correcting them.