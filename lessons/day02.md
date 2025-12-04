# Day 2 — Linear Formula Refresher: `y = m·x + b` (HVAC Warm‑Up Edition)

**Goal:** See how the classic line equation maps to *minutes vs ΔT* for building warm‑ups.

Day 2 recasts warm‑up as a simple line.  Once you recognise the slope and intercept hiding in your data, Model 0 and Model 1 suddenly make sense.

## 1.  What `y = m·x + b` Really Means

Everyone has seen the equation of a line, but here’s what each symbol represents in the context of optimal start:

* **`y`** → the **output**: predicted warm‑up time (`t`, in minutes).
* **`x`** → the **input**: usually ΔT, or sometimes ΔT squared (Model 1) or ΔT multiplied by a weather factor (Model 3).
* **`m`** → the **slope**: how many minutes the warm‑up takes per unit of `x`.  In Model 0 this is the inverse of degrees‑per‑minute.
* **`b`** → the **intercept**: the fixed overhead time you always incur — coil warm‑up, valve stroking, sensor lag, etc.

Written in warm‑up form:

```
t = a * DeltaT + b
```

Here `a` (minutes per degree) is just the **slope** and `b` (minutes) is the **intercept**.

## 2.  How It Applies to Optimal Start

If a building warms at **0.20 °F/min**, the inverse is **5 min per degree**.  A possible linear warm‑up model could be:

```
t = 5 * DeltaT + 7
```

…meaning it takes about 5 minutes for each degree plus 7 minutes of fixed overhead.  This linear form is the basis of PNNL’s Model 1 when `x = DeltaT` instead of `DeltaT²`.

## 3.  Slopes in HVAC Warm‑Up (Practical Intuition)

Suppose you record several warm‑ups:

```
DeltaT = 4°F  →  warm‑up 30 min  →  7.5 min/°F
DeltaT = 6°F  →  warm‑up 40 min  →  6.7 min/°F
DeltaT = 8°F  →  warm‑up 55 min  →  6.9 min/°F
```

The minutes‑per‑degree are not identical, but they’re close.  Averaging them gives a slope `m` of about **7 min/°F**.  You can then choose an intercept `b` to account for startup lag.

## 4.  Solve a Linear Model by Hand (Two Points)

Given two warm‑up datapoints:

* (ΔT = 2 °F, t = 15 min)
* (ΔT = 6 °F, t = 27 min)

Compute the slope `m`:

```
m = (27 − 15) / (6 − 2) = 12 / 4 = 3 min/°F
```

Then find the intercept `b` using one point (for example, 2 °F, 15 min):

```
b = 15 − 3 * 2 = 9 min
```

Your linear warm‑up model becomes:

```
t = 3 * DeltaT + 9
```

## 5.  Day 2 Micro‑Exercise

Try solving these:

1. **Compute the slope `m`** for points (ΔT = 3 °F, t = 14 min) and (ΔT = 7 °F, t = 32 min).
2. **Compute the intercept `b`** using the slope from (1) and one of the points.
3. **Predict warm‑up time** for ΔT = 5 °F using your line from (1) and (2).

## 6.  Key Takeaway From Day 2

Optimal‑start models often reduce to a simple line.  Identify the **slope** (minutes per degree) and the **intercept** (fixed overhead) and you can predict warm‑up times.  Model 1 and Model 3 are just variations on this theme with different definitions for `x` and a few extra terms.