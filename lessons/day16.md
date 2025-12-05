# Day 16 — The Reference Temperature (T_ref)

**Goal:** Define a baseline outdoor temperature used in Model 2 and explain its role.

## 1. Choosing a Baseline

In heating season, a common choice is `T_ref = 0 °F` — the coldest reasonable outdoor temperature.  In cooling, you might use `T_ref = 100 °F`.

## 2. Why It Matters

Model 2 adjusts the predicted warm‑up time by comparing yesterday’s outdoor temperature to today’s.  The “reference” anchors the ratio calculation.

## 3. Sensitivity

Pick `T_ref` too low and you’ll overcompensate in mild weather.  Pick it too high and you won’t compensate enough on cold days.

## 4. Key Takeaway

The reference temperature is a tuning knob.  Choose a value that reflects your climate extremes.
