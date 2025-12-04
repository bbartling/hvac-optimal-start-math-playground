# Day 25 — Implement Full Model Evaluation Logic

**Goal:** Bring together the prediction equations, coefficient storage and smoothing into a coherent workflow.

Today you’ll outline the entire sequence that an optimal‑start block performs each morning and after each warm‑up.  This “glue logic” is as important as the equations themselves.

## 1.  Before Warm‑Up (Prediction Phase)

1. Read current zone temperature (`T_zone,start`) and occupied setpoint (`T_setpoint`).
2. Compute `DeltaT = T_setpoint − T_zone,start`.
3. If using Model 3, read outdoor air temperature and compute `WF`.
4. Use the appropriate model equation:
   * **Model 0:** `minutesPredicted = DeltaT / rateEMA`
   * **Model 1:** `minutesPredicted = a * (DeltaT)^2 + b`
   * **Model 3:** `minutesPredicted = a*DeltaT + b*(DeltaT*WF) + d`
5. Subtract `minutesPredicted` from the scheduled occupancy start time to determine the optimal start time.

## 2.  After Warm‑Up (Learning Phase)

1. Measure actual warm‑up time (`actualMinutes`).  If the zone was already at setpoint, skip learning.
2. Compute the observed rate or observed coefficients:
   * **Model 0:** `observedRate = DeltaT / actualMinutes`
   * **Model 1:** derive `a_today` from `actualMinutes / (DeltaT)^2`
   * **Model 3:** derive `a_today`, `b_today` and `d_today` using the 3×3 system if enough datapoints exist
3. Update stored coefficients with smoothing factor α.
4. Store any new history record (for plotting or further analysis).

## Mini‑Exercises

1. Write pseudo‑code or a flowchart for a warm‑up sequence using Model 1, including prediction and update phases.
2. How would you modify the logic if the zone never drops below setpoint (e.g. in summer when cooling isn’t needed)?
3. In Model 3, if you detect the outdoor air sensor is faulty, how should your logic fall back?

## Key Takeaway

Optimal‑start isn’t just a formula; it’s a loop.  Each morning you compute a prediction, start the warm‑up at the right time, observe what happens, update your coefficients and repeat.  A clear implementation of this loop makes your system robust and maintainable.