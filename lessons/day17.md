# Day 17 — The Ratio Formula

**Goal:** Apply the weather ratio to adjust the base runtime

Model 2 multiplies the base warm‑up time by a ratio derived from outdoor
temperatures.  The formula is:

    ratio = (T_ref − OAT_yesterday) / (T_ref − OAT_today)

and the adjusted time is t_adj = t_base × ratio【913477360246089†L540-L554】.
If today is colder than yesterday the ratio exceeds 1, extending the
runtime; if today is warmer, the ratio shrinks the runtime.

## Python Mini‑Lesson

```python
# Compute the adjusted runtime given base time and outdoor temperatures
def adjusted_time(t_base, t_ref, oat_prev, oat_curr):
    ratio = (t_ref - oat_prev) / (t_ref - oat_curr)
    return t_base * ratio

t_base = 30.0
T_ref = 32.0
oat_prev, oat_curr = 25.0, 10.0
print(f'Adjusted time = {adjusted_time(t_base, T_ref, oat_prev, oat_curr):.1f} min')
```

## Exercises

1. For heating mode with T_ref=32°F, oat_prev=20°F and oat_curr=25°F, compute the ratio and adjusted time for t_base=40 min.
2. Describe a scenario where the ratio is exactly 1.0.  What does this mean physically?
3. Why does the ratio blow up as oat_curr approaches T_ref?

## Key Takeaway

The weather ratio stretches or shrinks the base runtime depending on how today’s outdoor temperature compares to yesterday’s.
