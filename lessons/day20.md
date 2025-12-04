# Day 20 — How Niagara Stores the Coefficients

**Goal:** See where the learned parameters live inside Niagara and how they persist across warm‑ups.

After you solve Model 1 or Model 3, you need to store the coefficients so they can be used the next morning.  Niagara’s ProgramObject has slots for this purpose.

## 1.  Slots for Model 0

Model 0 stores its single learned value in `degreesPerMinuteHeat` or `degreesPerMinuteCool` (depending on whether you’re heating or cooling).  Each time the EMA is updated, this slot changes.

## 2.  Slots for Model 1

The quadratic model needs two values:

* `model1CoeffA` — corresponds to `a` in `t = a*(DeltaT)^2 + b`
* `model1CoeffB` — corresponds to `b` (the intercept)

Each time new values are computed from the latest datapoints, these slots are blended with α just like the EMA.

## 3.  Slots for Model 3

Model 3 requires three slots:

* `model3CoeffA` — the `a` coefficient on ΔT
* `model3CoeffB` — the `b` coefficient on ΔT·WF
* `model3CoeffD` — the intercept `d`

Additionally you need to calculate and store the **weather factor** (WF) each morning, typically computed in a separate slot using outdoor air temperature.

## 4.  Updating the Slots

After each warm‑up, your code (or the Niagara block) should:

1. Compute new coefficients from today’s datapoints.
2. Blend them into the stored slots using `alpha` to avoid jumps.
3. Use the updated slots for tomorrow’s prediction.

## Mini‑Exercises

1. Imagine your current `model1CoeffA` is 0.85 and `model1CoeffB` is 8.0.  Today’s solved `a_today` and `b_today` are 1.1 and 6.0, with α = 0.2.  Compute the new stored coefficients.
2. In Model 3, why must you recompute WF every morning instead of storing it?

## Key Takeaway

Niagara persists the learned coefficients in dedicated slots.  Updating these slots with a smoothing factor makes the model adaptive but not erratic.  Understanding where these values live will help you troubleshoot and tune your optimal‑start ProgramObject.