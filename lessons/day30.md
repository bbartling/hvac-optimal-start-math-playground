# Day 30 — Final Project: Build a Mini Optimal‑Start Engine

**Goal:** Combine everything you’ve learned into a simple, end‑to‑end optimal‑start algorithm.

Congratulations on making it to Day 30!  Your final task is to put the pieces together and build a working miniature of an optimal‑start system.

## 1.  Outline of the Engine

1. Collect or generate a series of warm‑up events (`DeltaT`, `WF`, `actualMinutes`).
2. Choose a model (Model 0, 1, 3 or a hybrid).
3. Initialise the coefficients (`rateEMA` for Model 0, `a`, `b`, `d` for others).
4. For each event:
   * **Predict:** Compute `t_predicted` using the current coefficients.
   * **Update:** Compute observed values and update coefficients with smoothing.
   * **Log:** Record predictions, actuals and updated coefficients for analysis.

## 2.  Suggested Implementation Steps

* Start with Model 0 for simplicity.  Use a loop to process each event and update `rateEMA`.
* Extend to Model 1 by storing `a` and `b` and updating `a` as you go.  Optionally incorporate `b` updates when you have multiple points.
* Add weather by incorporating WF into your data and implementing the Model 3 update.
* Plot or print the prediction vs actual over time to see how the model improves.

## Mini‑Exercises

1. Write a Python script that reads a CSV of warm‑up data and runs Model 0 with α = 0.15.  Plot predicted vs actual times.
2. Extend your script to include Model 1 updates and compare the errors of the two models.
3. Reflect on which model performed best and why.  Are there mornings where any model struggled?  What would you try next?

## Key Takeaway

Building a mini optimal‑start engine cements your understanding of the mathematics and the workflow.  You now have the tools to deploy, evaluate and customise optimal‑start algorithms in your own buildings — and to continue refining them as you gather more data.