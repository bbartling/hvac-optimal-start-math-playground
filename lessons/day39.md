# Day 39 — Experiment: The “Cold Soak Multiplier”

**Goal:** Explore scaling Model 3 predictions by a factor (e.g., 1.2) to account for weekend cooling.

## 1.  The Multiplier Concept

Rather than adding a fixed time, you can multiply the predicted minutes by a constant greater than 1.  This “cold soak multiplier” scales with the predicted time — longer warm‑ups get a larger absolute boost.

For example:

```
t_monday = 1.3 * t_predicted
```

If the model predicts 40 minutes, Monday becomes 52 minutes.  If it predicts 90 minutes, Monday becomes 117 minutes.

## 2.  Determining the Factor

Collect several weeks of Monday data and calculate the ratio `actual / predicted` for each model.  Take the average ratio as your multiplier (e.g., 1.3).

## 3.  Micro‑Exercises

1. Using your data, compute the average `actual/predicted` ratio for Monday runs.  
2. Apply a multiplier based on that ratio to the next two Mondays.  Does the error decrease?  
3. Discuss whether a multiplier or fixed adder seems more appropriate for your building.

## 4.  Key Takeaway

Multiplying the prediction by a “cold soak factor” adapts the correction to the size of the problem, offering a more scalable solution than a fixed adder.
