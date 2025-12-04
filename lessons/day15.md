# Day 15 — PNNL Model 0 (Pure Linear EMA Model)

**Goal:** Formalise the simplest optimal‑start algorithm: degrees‑per‑minute divided into ΔT.

PNNL’s Model 0 (and Niagara’s default linear model) predicts warm‑up time as a straight line.  It uses an exponential moving average of degrees‑per‑minute for self‑tuning.

## 1.  Model Formula

```
t_predicted = DeltaT / rateEMA
```

Where:

* `DeltaT = T_setpoint − T_zone,start`
* `rateEMA` = current exponential moving average of degrees‑per‑minute

The runtime prediction is simply the temperature difference divided by the smoothed heating or cooling rate.

## 2.  EMA Update

After each warm‑up, compute the observed rate and blend it into `rateEMA` as described in Days 8–10.

## 3.  Strengths and Limitations

* **Strengths:** Easy to implement, minimal computation, reacts to changing building performance.
* **Limitations:** Assumes minutes per degree are constant regardless of ΔT.  May under‑predict on very cold mornings or over‑predict on very mild ones.

## Mini‑Exercises

1. If `rateEMA = 0.22 °F/min` and `DeltaT = 6 °F`, compute the predicted warm‑up time.
2. After a warm‑up of ΔT = 5 °F in 24 min, update `rateEMA` using α = 0.1 and initial `rateEMA = 0.22`.

## Key Takeaway

Model 0 is the baseline.  It predicts warm‑up time by dividing the temperature gap by a learned rate.  For buildings with mild set‑backs or stable envelopes, Model 0 can be sufficient; for more challenging sites, you’ll need the curvature and weather adjustments provided by Models 1 and 3.