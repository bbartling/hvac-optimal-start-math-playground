# Day 10 — How Niagara’s Optimal Start Uses EMA

**Goal:** See exactly where the EMA appears in Model 0 and how it drives the start prediction.

In Niagara’s Optimal Start block, the **degrees‑per‑minute rate** is not fixed.  It’s an exponential moving average that updates each time a warm‑up completes.

## 1.  Observed Rate and EMA Update

After a warm‑up finishes, the block measures how far the zone temperature travelled and how long it took.  The **observed rate** is:

```
observedRate = DeltaT / actualMinutes
```

Then the EMA is updated:

```
rateEMA = rateEMA + alpha * (observedRate − rateEMA)
```

This new `rateEMA` is stored in slots like `degreesPerMinuteHeat` or `degreesPerMinuteCool`.  It’s the learned average heating/cooling rate.

## 2.  Prediction Using the EMA

Each morning, before the warm‑up starts, the block computes how long it *thinks* it will take:

```
DeltaT = abs(setpoint − zoneStart)
minutesPredicted = DeltaT / rateEMA
```

That predicted time drives the start command: the block subtracts `minutesPredicted` from the scheduled occupancy time to decide when to enable heating or cooling.

## Mini‑Exercises

1. Yesterday’s rateEMA is 0.25 °F/min.  Today’s warm‑up: ΔT = 5 °F, actualMinutes = 18.  With α = 0.2, compute the new rateEMA.
2. Using your new rateEMA from (1), predict the warm‑up time for ΔT = 4 °F.

## Key Takeaway

Niagara’s linear Model 0 is essentially one division and one EMA update.  The block learns a heating or cooling rate by blending in each day’s observed rate and uses that average to schedule the next warm‑up.