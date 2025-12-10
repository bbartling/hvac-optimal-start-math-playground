# Day 1 — The Basics: ΔT and Rate

**Goal:** Understand temperature difference and rate of change in HVAC warm‑up

## 1. Concept and Definitions

Optimal start begins with two simple quantities: the temperature difference (ΔT)
between the desired set point and the current zone temperature, and the rate
at which the zone warms or cools.  ΔT is just subtraction, and the rate is
computed as ΔT divided by the time it took to achieve that change.  Knowing
both quantities allows you to predict how long the system needs to run to
reach set point.

In HVAC, we often express the rate in degrees per minute (°F/min).  A small
ΔT with a slow rate results in a longer preheat, while a large ΔT with a
rapid rate leads to a shorter preheat.

## 2. How to Use It

Apply the concepts above using the formula or algorithm provided. Refer to the mini examples below for a demonstration.

## 3. Why This Matters

Understanding this concept allows you to build more accurate and efficient optimal‑start models, improving comfort and energy savings.

## 4. Mini‑Examples

Here's a simple Python demonstration:

```python
# Compute ΔT and rate of change
setpoint = 72.0
zone_start = 65.0
delta_t = setpoint - zone_start  # degrees F

time_minutes = 35
rate = delta_t / time_minutes  # degrees per minute

print(f'DeltaT = {delta_t:.1f} °F')
print(f'Rate   = {rate:.3f} °F/min')
```

## 5. Micro‑Exercises

1. Compute ΔT for a zone at 67 °F with a set point of 74 °F.
2. A zone warms from 64 °F to 72 °F in 30 minutes.  What is the rate of change?
3. If ΔT = 6 °F and the rate is 0.25 °F/min, how many minutes will it take to reach set point?
4. Create a simple Python file that performs the calculations from this lesson.
   Use only basic variables, arithmetic, print statements and at most a `for` loop over a list. Avoid defining functions or using `zip`.
   Hint: replicate the structure of the examples above but use your own numbers or dataset.

## 6. Key Takeaway

ΔT and rate are the foundation of all optimal start models.  Without these two numbers, you cannot estimate warm‑up time.
