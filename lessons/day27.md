# Day 27 — Compare Accuracy of the Models

**Goal:** Learn how to evaluate Model 0, Model 1 and Model 3 on historical data and decide which performs best.

Once you’ve implemented and tuned your models, you need to measure how well they’re doing.  Day 27 gives you a framework for comparing predictions against actual warm‑up times.

## 1.  Error Metrics

* **Absolute error:** `abs(t_actual − t_predicted)` — easy to interpret in minutes.
* **Relative error:** `(t_actual − t_predicted) / t_actual` — helpful when comparing days with different run times.
* **Mean absolute error (MAE):** average of absolute errors across many mornings.

## 2.  Evaluation Process

1. Assemble a set of historical warm‑up datapoints (`DeltaT`, `WF`, `t_actual`).
2. For each model:
   * Predict `t_predicted` using the current coefficients.
   * Compute the chosen error metric.
3. Compare the average error across models.

## 3.  Sensitivity Analysis

* Examine how errors change with ΔT.  Does one model under‑predict for large ΔT?
* Examine how errors change with WF.  Does Model 3 perform better on cold mornings?

## Mini‑Exercises

1. Create a small table of five warm‑up events with ΔT, WF, and actual time.  Compute predictions using a sample Model 0 and Model 1 and calculate the absolute error.
2. Plot error vs ΔT for Model 0 and Model 1 (a simple spreadsheet chart is fine).  Which model’s error grows faster with ΔT?
3. If Model 3 shows little improvement over Model 1, what might that suggest about the weather effect on this building?

## Key Takeaway

Evaluation closes the loop: you don’t know which model is best until you compare predictions to reality.  Use simple error metrics, look at performance across ΔT and WF ranges, and let the data guide your model choice.