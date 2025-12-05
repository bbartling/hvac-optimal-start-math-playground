# Day 35 — Week 5 Review: The Full Arsenal

**Goal:** Summarise the strengths and weaknesses of all five models and reflect on which is best for your site.

## 1.  Recap of Models

* **Model 0 (Linear EMA):** Fast and simple.  Great for mild climates or small ΔT.  Fails when the rate isn’t constant.  
* **Model 1 (Quadratic):** Handles deep setbacks better by accounting for increasing difficulty as ΔT grows.  Needs regression and two parameters.  
* **Model 2 (Weather Adjusted):** Adds a simple outdoor correction.  Good for perimeter zones but still linear in nature.  
* **Model 3 (Multiple Regression):** Uses both ΔT and a weather factor to fit a plane.  Offers high accuracy but requires matrix math and lots of data.  
* **Model 4 (Logarithmic):** Models exponential approach to setpoint.  Ideal for systems that slow down as they get close.

## 2.  How to Choose

1. **Start simple**: Try Model 0 and see if the building is roughly linear.  
2. **Look at ΔT range**: If deep setbacks (> 8°F) are common, consider Model 1.  
3. **Check OAT influence**: Large swings in outdoor temperature call for Model 2 or 3.  
4. **Observe the shape**: If error decays exponentially, Model 4 may capture it best.  
5. **Hybrid rules**: You can mix models (e.g., Model 0 for small ΔT and Model 3 for large ΔT) to handle different regimes.

## 3.  Micro‑Exercises

1. Create a comparison table for your site showing the mean absolute error (MAE) of each model over the last 20 mornings.  
2. Identify at least one scenario where each model produces the worst error.  
3. Suggest a hybrid control logic tailored to your building, using the strengths of each model.

## 4.  Key Takeaway

There is no one‑size‑fits‑all model.  Understanding the underlying physics and data behaviour allows you to pick or combine models wisely.
