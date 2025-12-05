# Day 21 — Compare Linear, Quadratic and Weather Models

**Goal:** Learn when to choose Model 0, Model 1 or Model 3 and what trade‑offs each entails.

No single model fits every building.  The best model depends on your climate, envelope, setback strategy and available sensors.  Today you’ll compare the three options.

## 1.  Model 0 (Linear EMA)

* **Use when:** Setbacks are mild (ΔT usually < 6 °F) and the building warms consistently regardless of outdoor temperature.
* **Pros:** Simplest to implement, minimal calculation, adapts to gradual changes.
* **Cons:** Under‑predicts on very cold days or after deep setbacks; over‑predicts on mild mornings.

## 2.  Model 1 (Quadratic)

* **Use when:** The building warms significantly slower for large ΔT.  Cold mornings take disproportionately longer than mild mornings at the same ΔT.
* **Pros:** Captures curvature without external sensors; still easy to implement (only two coefficients).
* **Cons:** Ignores weather; may still mis‑predict if a 10 °F setback is combined with a very cold OAT.

## 3.  Model 3 (Weather‑Adjusted)

* **Use when:** Outdoor air temperature dramatically affects warm‑up speed.  A 6 °F setback at 40 °F warms faster than the same setback at 10 °F.
* **Pros:** Adjusts runtime for weather; more accurate across seasons.
* **Cons:** Requires an outdoor air temperature sensor; solving the 3×3 system adds complexity; still assumes a linear relationship with WF.

## Mini‑Exercises

1. A building in a warm climate rarely sees ΔT above 4 °F.  Which model would you choose and why?
2. A building in the Midwest has setbacks up to 10 °F and winters reach 5 °F.  Which model is likely best?
3. If you have Model 1 but you add an outdoor air sensor, how could you evolve the model?

## Key Takeaway

Model selection is an engineering judgment.  Start simple with Model 0, add curvature with Model 1 if cold mornings are slow, and incorporate weather with Model 3 if outdoor temperature is a major factor.  Each added term increases accuracy at the cost of complexity.