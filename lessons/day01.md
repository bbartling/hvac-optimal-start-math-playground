# Day 1 — Δ (Delta), Rate‑of‑Change & Degrees‑Per‑Minute (DPM)

**30‑Day Crash Course: Self‑Tuning Algebraic Models & EMA**

Day 1 lays the foundation.  It focuses on **what changes** (Δ), **how fast it changes** (rate) and how those concepts relate to the degree‑per‑minute numbers in Niagara’s Model 0.  No heavy algebra — just intuition, definitions and a few tiny exercises.

## 1.  What “Δ” Actually Means (BAS + HVAC version)

In HVAC and BAS work, **Δ (delta)** simply means: **“How much did something change?”**  It’s nothing more than subtraction.

For optimal‑start problems we care about temperature difference, so we define:

```
DeltaT = T_setpoint − T_zone,start
```

…where `T_setpoint` is your occupied setpoint and `T_zone,start` is the building temperature when the warm‑up begins.  That’s it — delta is just a difference.

## 2.  Rate of Change (Slope) Refresher

Warm‑up is all about **how fast** the temperature rises.  We measure that in degrees per minute:

```
Rate = DeltaT / DeltaTime
```

In Niagara’s Model 0, the **rate of temperature change** is literally the **degree‑per‑minute (DPM)** slot (`degreesPerMinute`).

## 3.  Why This Matters for Optimal Start

If you know:

* how many degrees you are away from your setpoint (`DeltaT`), and
* how many degrees per minute the building can warm (`Rate`),

then you can predict the warm‑up time with a simple division:

```
t = DeltaT / Rate
```

This single relationship forms the entire basis of **Model 0 (Linear EMA model)**.

## 4.  Mini‑Examples (super quick)

### Example A — Compute ΔT
Zone = 65 °F, Setpoint = 72 °F

```
DeltaT = 72 − 65 = 7 °F
```

### Example B — Compute rate‑of‑change (DPM)
Start = 65 °F, End = 72 °F, Time = 35 minutes

```
DeltaT = 7 °F
Rate   = 7 / 35 = 0.20 °F/min
```

### Example C — Predict warm‑up time
ΔT = 4 °F, Rate = 0.20 °F/min

```
t = 4 / 0.20 = 20 minutes
```

## 5.  Day 1 Micro‑Exercise

Try these on your own (you can use a calculator or pencil):

1. **Compute ΔT:** Zone = 67 °F, Setpoint = 72 °F.  What is `DeltaT`?
2. **Compute Rate:** Start = 64 °F, End = 72 °F, Time = 30 minutes.  What is the warm‑up rate?
3. **Predict Warm‑Up Time:** ΔT = 6 °F, Rate = 0.25 °F/min.  How many minutes will it take to reach setpoint?

## 6.  Key Takeaway From Day 1

Optimal‑start math is built on just two core ideas:

* **Temperature difference (ΔT):** how many degrees you need to go.
* **Warm‑up rate (°F per minute):** how fast the building can respond.

Everything else — the EMA learning, regression, and self‑tuning — builds directly on these two concepts.