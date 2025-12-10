# Day 16 — The Reference Temperature (T_ref)

**Goal:** Choose an appropriate baseline for the weather ratio

The ratio in Model 2 uses a reference outdoor temperature T_ref.  According
to the PNNL paper, T_ref is set to 0 °C (32 °F) for heating and 37.78 °C
(100 °F) for cooling【913477360246089†L514-L554】.  T_ref represents a
"worst‑case" condition where the equipment must run continuously.  The
ratio is calculated as (T_ref − OAT_yesterday)/(T_ref − OAT_today).
Choosing an appropriate T_ref ensures the ratio scales the runtime
correctly.

## Python Mini‑Lesson

```python
# Compute the ratio for heating mode using T_ref=32°F
T_ref = 32.0
oat_prev = 20.0
oat_curr = 15.0
ratio = (T_ref - oat_prev) / (T_ref - oat_curr)
print(f'Heating ratio = {ratio:.2f}')

# Compute the ratio for cooling mode using T_ref=100°F
T_ref_cool = 100.0
oat_prev = 85.0
oat_curr = 90.0
ratio_cool = (T_ref_cool - oat_prev) / (T_ref_cool - oat_curr)
print(f'Cooling ratio = {ratio_cool:.2f}')
```

## Exercises

1. Why is the ratio >1 when today is colder than yesterday (heating mode)?
2. How would you pick T_ref for a climate with very mild winters?
3. What happens if today’s outdoor temperature equals T_ref?

## Key Takeaway

T_ref anchors the weather ratio.  Selecting an appropriate value based on heating or cooling mode ensures the ratio scales runtimes realistically.
