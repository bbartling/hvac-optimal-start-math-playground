# Day 1 — Δ (Delta), Rate‑of‑Change & Degrees‑Per‑Minute (DPM)

**Goal:** Lay the foundation by understanding what changes (Δ), how fast it changes (rate), and how those concepts relate to the degree‑per‑minute numbers in Model 0.

## 1. What “Δ” Actually Means (BAS + HVAC)

In building automation, **Δ (delta)** simply measures a change.  For optimal start we care about the temperature difference between the setpoint and the current zone temperature.  Define it as:

```
DeltaT = T_setpoint - T_zone,start
```

where `T_setpoint` is your occupied setpoint and `T_zone,start` is the zone temperature when warm‑up begins.

## 2. Rate of Change (Slope)

Warm‑up is all about how fast the temperature rises.  The **rate** is measured in degrees per minute:

```
Rate = DeltaT / DeltaTime
```

In Niagara’s Model 0, this is the **degree‑per‑minute** slot (`degreesPerMinute`).

## 3. Why This Matters

If you know how far you are from setpoint (`DeltaT`) and how fast you can close that gap (`Rate`), then you can predict the warm‑up time:

```
t = DeltaT / Rate
```

This simple relationship is the entire basis of **Model 0**.

## 4. Mini‑Examples

* *Compute ΔT:* Zone = 65 °F, Setpoint = 72 °F → `DeltaT = 72 - 65 = 7 °F`.
* *Compute Rate:* Start = 65 °F, End = 72 °F, Time = 35 min → `Rate = 7/35 = 0.20 °F/min`.
* *Predict Warm‑Up:* ΔT = 4 °F, Rate = 0.20 °F/min → `t = 4/0.20 = 20 min`.

## 5. Micro‑Exercises

1. Compute ΔT if the zone is 67 °F and setpoint is 72 °F.
2. Compute the warm‑up rate for 64 °F rising to 72 °F in 30 min.
3. Predict warm‑up time for ΔT = 6 °F at 0.25 °F/min.

## 6. Key Takeaway

Optimal‑start math is built on just two core ideas: **temperature difference** (ΔT) and **warm‑up rate** (°F/min).  Everything else — EMA, regression, self‑tuning — builds from these.
