# Day 15 — Why Indoor Temp isn’t Enough

**Goal:** Recognise that outdoor conditions affect warm‑up

For perimeter zones exposed to the weather, indoor temperature alone
doesn’t capture how quickly a space will warm.  Cold outdoor air can
continue to steal heat during warm‑up, slowing the response.  Model 2
introduces an outdoor temperature adjustment to compensate for this
effect【913477360246089†L514-L554】.

## Python Mini‑Lesson

```python
# Demonstrate how colder outdoor air increases predicted time
delta_t = 6.0
base_rate = 0.20  # °F/min
t_base = delta_t / base_rate
for diff in [0, -10, -20]:
    # diff is the drop in outdoor temperature compared to yesterday (°F)
    ratio = (100 - (70 + diff)) / (100 - 70)  # using T_ref=100°F as in cooling mode
    t_adj = t_base * ratio
    print(f'Outdoor drop={diff:+}°F → ratio={ratio:.2f}, time={t_adj:.1f} min')
```

## Exercises

1. Explain why colder outdoor conditions result in a ratio greater than 1.
2. What happens if today is warmer than yesterday?
3. Which zones (interior or perimeter) benefit most from Model 2?

## Key Takeaway

Outdoor air temperature can significantly alter warm‑up time.  Model 2 corrects the base runtime using a weather‑dependent ratio.
