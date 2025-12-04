# Day 12 — EMA as a Control Loop Gain

**Goal:** Understand the role of the smoothing factor α in the EMA and how it parallels control system gain.

In PID control loops, gain determines how aggressively the controller responds to error.  In an EMA, the **α parameter** plays a similar role: it sets the “learning rate” of the moving average.

## 1.  Interpreting α

* **Small α (e.g. 0.05):** Each new observation moves the average only a little.  The EMA is stable but slow to adapt.
* **Medium α (e.g. 0.2):** New observations have moderate influence.  A good compromise for most buildings.
* **Large α (e.g. 0.7):** The EMA follows each new observation closely.  It adapts quickly but may become noisy or unstable if the data are erratic.

Choosing α is like tuning a loop gain.  Too low and the model lags; too high and predictions jump around.

## 2.  Example Sensitivity

Suppose the current EMA is 0.20 °F/min and the next observed rate is 0.30 °F/min.

* With α = 0.05: `EMA_new = 0.20 + 0.05 * (0.30 − 0.20) = 0.205` (barely changes).
* With α = 0.50: `EMA_new = 0.20 + 0.50 * (0.30 − 0.20) = 0.25` (big jump).

You can see how α changes the sensitivity.

## Mini‑Exercises

1. The EMA is 0.15 °F/min.  The next observed rate is 0.12 °F/min.  Compute `EMA_new` for α = 0.1, 0.3 and 0.8.  Compare how much the average moves.
2. If your optimal‑start model is too jumpy from day to day, what should you do with α?
3. If the model always seems slow to respond to weather changes, what should you do with α?

## Key Takeaway

The smoothing factor α is the “gain” of the EMA.  Tune it carefully: low α values provide stability; high α values increase responsiveness.  Most BAS implementations choose α between 0.05 and 0.30 for optimal start.