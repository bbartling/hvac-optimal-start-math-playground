# Day 28 — Identify Pathological Cases

**Goal:** Recognise situations where optimal‑start models break down and how to handle them.

Not every morning is a clean warm‑up.  Some days yield misleading datapoints that can corrupt your model if you don’t detect them.

## 1.  Zero or Negative ΔT

If the zone starts at or above setpoint, there’s nothing to learn.  Skip updating your model when:

```
DeltaT <= 0
```

Updating on tiny ΔT values (e.g. < 1 °F) can also introduce noise; consider ignoring them.

## 2.  Zero Runtime

If the warm‑up time is zero or very short, perhaps because the system was already running or the setpoint changed mid‑day, computing `observedRate` will give an infinite or unrealistic value.  Detect and discard these cases.

## 3.  Staging and Lockouts

Multi‑stage equipment may run in low stage for the first part of warm‑up then ramp to high stage.  Lockout conditions (e.g. economiser lockout) can cause unusual warm‑up behaviour.  These datapoints may not represent normal operation.

## 4.  Sensor Errors and Overrides

Bad sensors, manual overrides or sudden setpoint changes mid‑run distort warm‑up data.  Cross‑check against alarms and override logs before using a datapoint.

## Mini‑Exercises

1. Make a list of at least five reasons to skip learning from a warm‑up event.
2. Write pseudo‑code to detect and discard events where `DeltaT` is less than 1 °F or `actualMinutes` is less than 5.
3. How might you detect an economiser lockout affecting warm‑up in your logs?

## Key Takeaway

Robust self‑tuning isn’t just about the math — it’s about data hygiene.  Recognise and skip pathological cases (zero ΔT, zero runtime, sensor errors, unusual modes) so your model learns from meaningful data.