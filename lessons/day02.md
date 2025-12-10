# Day 2 — The Formula: t = ΔT / rate

**Goal:** Use the simplest linear formula to estimate warm‑up time

## 1. Concept and Definitions

When the rate of temperature change is roughly constant, the warm‑up time
(t) can be approximated by dividing the temperature difference by the rate:

t = ΔT / rate.

This equation is simply a rearrangement of the definition of rate.  It is the
basis of the PNNL Model 0 (linear EMA).  In practice you compute ΔT from
the current conditions and divide by a smoothed rate (see the following
lessons) to avoid jitter.

## 2. How to Use It

Apply the concepts above using the formula or algorithm provided. Refer to the mini examples below for a demonstration.

## 3. Why This Matters

Understanding this concept allows you to build more accurate and efficient optimal‑start models, improving comfort and energy savings.

## 4. Mini‑Examples

Here's a simple Python demonstration:

```python
# Predict warm‑up time using t = ΔT / rate
delta_t = 5.0   # degrees F
rate = 0.20     # degrees per minute
time_est = delta_t / rate
print(f'Predicted time = {time_est:.1f} minutes')
```

## 5. Micro‑Exercises

1. If ΔT = 8 °F and the rate is 0.25 °F/min, compute the predicted warm‑up time.
2. A building warms 10 °F in 40 minutes.  Predict the time to warm 6 °F assuming the same rate.
3. Explain why simply dividing by today’s rate may lead to poor predictions on some days.
4. Create a simple Python file that performs the calculations from this lesson.
   Use only basic variables, arithmetic, print statements and at most a `for` loop over a list. Avoid defining functions or using `zip`.
   Hint: replicate the structure of the examples above but use your own numbers or dataset.

## 6. Key Takeaway

Dividing ΔT by the warm‑up rate gives a quick estimate of run time.  It’s the starting point for more advanced models.
