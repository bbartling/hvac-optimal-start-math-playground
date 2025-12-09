# Day 49 — The "Monday Neuron" (Interpreting Weights)

**Goal:** Understand how the weights you trained actually solve the Monday Cold Soak problem automatically.

## 1. The Final Formula

After training, your model is no longer a "black box." It is just a math formula with specific numbers plugged in.

$$
\text{Time} = (w_1 \cdot \Delta T) + (w_2 \cdot \text{IsMonday}) + \text{Bias}
$$

## 2. Reading the Mind of the Machine

We can inspect the final values of $w_1$ and $w_2$ to understand what the AI "learned."

* **$w_1$ (Temp Weight):** This is your standard "Minutes per Degree" (just like Model 0). If $w_1 = 5.0$, it means every degree of warm-up takes 5 minutes.
* **$w_2$ (Monday Weight):** This value is the **AI-discovered Cold Soak Adder**.

If your trained model outputs $w_2 = 45.0$, it means the math *automatically* decided that Mondays need exactly 45 extra minutes to reach the setpoint. You didn't code an `IF` statement; the Gradient Descent process found the correlation between the "Monday Flag" and the "Higher Error" and assigned a weight to fix it.

## 3. Micro‑Exercises

1.  Train a model on the dataset from Day 47 (yesterday's lesson).
2.  Print the final weights using `print(weights)`.
3.  Compare the learned $w_2$ to the "Technician's Guess" from Day 38. Did the AI find a similar buffer (e.g., 60 minutes), or did it find something more precise (e.g., 42 minutes)?

## 4. Key Takeaway

In AI, the weights *are* the logic. $w_2$ isn't just a random number; it is the encoded physical reality of the weekend cold soak.
