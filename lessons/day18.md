# Day 18 — Calculating the Base Rate (α₂,a)

**Goal:** Derive the indoor rate before applying the weather adjustment

## 1. Concept and Definitions

Model 2 first computes a base rate α₂,a from yesterday’s warm‑up data.
The PNNL paper defines α₂,a as (T_sp − T_z,0)/Δt_k−1, essentially the
inverse of the minutes per degree【913477360246089†L540-L554】.  This
value captures how quickly the zone warmed yesterday before any weather
adjustment.  You then use α₂,a to predict today’s base time and multiply
it by the ratio from Day 17.

## 2. How to Use It

Apply the concepts above using the formula or algorithm provided. Refer to the mini examples below for a demonstration.

## 3. Why This Matters

Understanding this concept allows you to build more accurate and efficient optimal‑start models, improving comfort and energy savings.

## 4. Mini‑Examples

Here's a simple Python demonstration:

```python
# Compute α₂,a from yesterday’s data and predict today’s base time
delta_t_yesterday = 8.0  # °F increase yesterday
time_yesterday = 40.0    # minutes
alpha_2a = delta_t_yesterday / time_yesterday
# Predict base time for today
delta_t_today = 6.0
t_base_today = delta_t_today / alpha_2a
print(f'α₂,a = {alpha_2a:.3f} °F/min')
print(f'Base time today = {t_base_today:.1f} minutes')
```

## 5. Micro‑Exercises

1. If yesterday’s ΔT=10 °F and time=45 min, compute α₂,a.
2. Predict the base runtime for ΔT=5 °F using your α₂,a.
3. Why is α₂,a essentially the same as the linear rate used in Model 0?
4. Create a simple Python file that performs the calculations from this lesson.
   Use only basic variables, arithmetic, print statements and at most a `for` loop over a list. Avoid defining functions or using `zip`.
   Hint: replicate the structure of the examples above but use your own numbers or dataset.

## 6. Key Takeaway

Calculating α₂,a isolates the indoor heating behaviour from the weather.  It provides a baseline that is later corrected by the outdoor ratio.
