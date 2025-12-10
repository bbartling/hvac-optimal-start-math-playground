# Day 8 — Why Heat Transfer isn’t Linear

**Goal:** Recognise that warm‑up time grows faster than ΔT

In many buildings the last few degrees take longer than the first.  This
non‑linear behaviour occurs because heat transfer slows as the zone
approaches set point; the walls, furniture and air must all warm up.
PNNL’s Model 1 captures this by squaring the temperature difference:
t = α₁,a × (ΔT)² + α₁,b 【913477360246089†L448-L476】.  The square term
makes the runtime grow rapidly with large ΔT, better matching reality.

## Python Mini‑Lesson

```python
# Compute warm‑up time using a quadratic model
delta_t = 6.0
alpha_a = 1.5  # minutes per (degree)^2
alpha_b = 2.5  # minutes
t_pred = alpha_a * (delta_t ** 2) + alpha_b
print(f'Predicted time = {t_pred:.1f} minutes')
```

## Exercises

1. Using α₁,a=1.0 and α₁,b=3.0, compute predicted times for ΔT=4 °F and ΔT=8 °F.
2. Explain why squaring ΔT exaggerates large temperature differences.
3. Give an example of a high‑mass zone where Model 1 would outperform Model 0.

## Key Takeaway

Quadratic models reflect the slowing heat transfer near set point.  The (ΔT)² term makes large setbacks require disproportionately longer preheat times.
