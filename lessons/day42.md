# Day 42 — Final Project: Monday Showdown

**Goal:** Put all the theory into practice by comparing model predictions to actual Monday warm‑up data.

## 1.  Gather Data

Collect at least five Monday warm‑up events from your building.  For each, record:

* Start zone temperature (`T_zone,start`)
* Setpoint temperature (`T_sp`)
* Outdoor air temperature (`T_oat`)
* Actual minutes to setpoint

## 2.  Compare Predictions

For each event, compute predictions using:

1. **Model 3 only** — use the coefficients learned from weekday data.  
2. **Technician’s guess** — add a fixed buffer (e.g., +60 minutes).  
3. **Cold soak multiplier** — multiply the Model 3 prediction by your `alpha_factor` (e.g., 1.3).

## 3.  Analyse the Results

Compute the error for each method (predicted – actual).  Which method gives the smallest average error?  Which one has the biggest worst‑case error?  Plot the results if possible.

## 4.  Write a Short Report

Summarise your findings in 1–2 paragraphs.  Discuss whether the extra complexity of Model 3 plus a multiplier is justified compared to the simplicity of a fixed adder.

## 5.  Key Takeaway

Real data will tell you which Monday strategy works best.  Testing and tuning are essential to delivering both comfort and energy savings.
