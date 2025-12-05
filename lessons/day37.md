# Day 37 — Why Math Fails Here

**Goal:** Explain why standard regression and smoothing techniques can’t capture the weekend effect.

## 1.  Dependence on Recent History

All self‑tuning models rely on the last few mornings to learn the building’s behaviour.  Over the weekend, nothing happens — there are no fresh data points for 48 hours.  Monday’s run is fundamentally different from the short runs seen Tuesday through Friday.  

## 2.  Mismatch of Conditions

* Thermal mass is colder.  
* Humidity may have equilibrated differently.  
* Outdoor temperatures might have varied significantly over two days.  

These factors mean Monday should be treated as its own class of problem, not just another day.

## 3.  Micro‑Exercises

1. Fit a Model 3 to your Tuesday–Friday data.  Use it to predict Monday.  Compute the percentage error.  
2. Repeat with Models 0–2.  Which model performs “least bad” on Monday?  
3. Write a short paragraph on why adding more history (e.g., 20 days) still doesn’t fix Monday predictions.

## 4.  Key Takeaway

Monday warm‑ups don’t obey the same statistical patterns.  Treating them separately avoids erroneous predictions.
