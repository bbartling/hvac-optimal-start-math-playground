# Day 9 — The Dead Time Intercept (b)

**Goal:** Explain the intercept term b and why systems run for several minutes before sensors register a temperature change.

## 1. Why Warm‑Up Appears Delayed

When the unit first turns on, the heating coil warms up, the fan ramps, and ducts begin to heat.  The zone sensor may not see a temperature rise for 5–10 minutes.

## 2. Intercept `b`

In the quadratic model:

```
t = a * (DeltaT)^2 + b
```

The term `b` captures this **dead time**.  It’s the minutes of warm‑up that are independent of ΔT.  Larger `b` values indicate slower sensor or coil response.

## 3. Example

If `a = 0.5` and `b = 8`, then even a ΔT of zero would predict `t = 8` minutes.  That’s the time it takes for the system to start impacting the zone.

## 4. Exercise

Measure how long your system runs before the zone temperature moves.  Use that as an initial estimate of `b`.

## 5. Key Takeaway

The intercept term accounts for sensor lag and equipment inertia.  Ignoring `b` will underestimate the warm‑up time.
