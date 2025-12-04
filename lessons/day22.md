# Day 22 — Building an Optimal‑Start Dataset

**Goal:** Learn what data you need to collect to train and tune your models effectively.

Models are only as good as the data you feed them.  Day 22 focuses on assembling a clean, representative warm‑up dataset.

## 1.  Required Data Points

For each morning warm‑up you should capture:

* **Start time:** When the warm‑up begins.
* **Start zone temperature:** `T_zone,start`.
* **Occupied setpoint:** `T_setpoint`.
* **Warm‑up end time:** When the zone hits setpoint.
* **Outdoor air temperature (OAT):** For Model 3 weather factor.

From these you can compute:

* `DeltaT = T_setpoint − T_zone,start`
* `Warm‑Up Time = End time − Start time` (minutes)
* `WF` if using Model 3.

## 2.  Data Cleaning

* **Remove holidays:** Occupancy may be different and schedules may be off.
* **Discard sensor faults:** If a temperature sensor fails or reads obviously wrong, skip that day.
* **Consistent setpoints:** Ensure the occupied setpoint hasn’t been changed mid‑run.
* **Exclude partial warm‑ups:** Days when the building was already at setpoint or when warm‑up was interrupted by alarms or operator intervention.

## 3.  Ideal Sample Size

For Model 0 an EMA updates continuously, so you don’t need to batch data.  For Models 1 and 3, aim for at least 5–10 representative mornings to compute initial coefficients.  More data helps average out noise.

## Mini‑Exercises

1. List three reasons you might discard a morning’s warm‑up from your dataset.
2. How could you automate data collection in Niagara (e.g. using histories or wire sheet blocks)?
3. If a building’s setpoint changes from 72 °F to 74 °F mid‑winter, how should you adjust your dataset and model?

## Key Takeaway

Good data is the foundation of accurate predictions.  Record zone start temperature, setpoint, run time and OAT consistently.  Clean outliers and special days.  With a solid dataset, the math from earlier lessons will pay off in reliable model coefficients.