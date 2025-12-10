# Day 20 — Sensitivity Check

**Goal:** Explore how changes in outdoor temperature impact the ratio

The weather ratio magnifies or reduces the predicted time depending on
how much colder or warmer today is relative to yesterday.  A sensitivity
check evaluates how big the effect is.  For example, a 10 °F colder day
might lengthen the runtime by 20 %, while a 10 °F warmer day might
shorten it.  Understanding this sensitivity helps set realistic limits on
the model’s output.

## Python Mini‑Lesson

```python
# Evaluate ratio sensitivity for heating mode
T_ref = 32.0
oat_prev = 25.0
for oat_curr in [15.0, 20.0, 25.0, 30.0]:
    ratio = (T_ref - oat_prev) / (T_ref - oat_curr)
    print(f'Today OAT={oat_curr}°F → Ratio={ratio:.2f}')
```

## Exercises

1. Plot the ratio as a function of today’s OAT for fixed oat_prev and T_ref.
2. At what temperature difference does the ratio become extremely large?
3. How could you modify Model 2 to cap the ratio when the difference is extreme?

## Key Takeaway

Sensitivity checks reveal how weather swings translate into runtime changes.  They also expose cases where the ratio might need clamping.
