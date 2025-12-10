# Day 18 — Calculating the Base Rate (α₂,a)

**Goal:** Derive the indoor rate before applying the weather adjustment

Model 2 first computes a base rate α₂,a from yesterday’s warm‑up data.
The PNNL paper defines α₂,a as (T_sp − T_z,0)/Δt_k−1, essentially the
inverse of the minutes per degree【913477360246089†L540-L554】.  This
value captures how quickly the zone warmed yesterday before any weather
adjustment.  You then use α₂,a to predict today’s base time and multiply
it by the ratio from Day 17.

## Python Mini‑Lesson

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

## Exercises

1. If yesterday’s ΔT=10 °F and time=45 min, compute α₂,a.
2. Predict the base runtime for ΔT=5 °F using your α₂,a.
3. Why is α₂,a essentially the same as the linear rate used in Model 0?

## Key Takeaway

Calculating α₂,a isolates the indoor heating behaviour from the weather.  It provides a baseline that is later corrected by the outdoor ratio.
