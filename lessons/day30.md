# Day 30 — The Logarithm (ln)

**Goal:** Explain why natural logarithms are used in Model 4 and derive the formula for predicting time.

## 1. Why ln?

The solution to a first‑order differential equation involves the natural logarithm.  If error decays exponentially (`error(t) = error0 * c^t`), then solving for `t` yields a logarithm.

## 2. Model 4 Formula

In Model 4:

```
t = ln(alpha_a / alpha_b) / ln(alpha_c)
```

where:
* `alpha_a` is the deadband (acceptable error),
* `alpha_b` is the initial error (DeltaT),
* `alpha_c` is the decay factor (learned from history).

## 3. Python Example

```python
import math
alpha_a = 0.5  # deadband, °F
alpha_b = 8.0  # current DeltaT, °F
alpha_c = 0.9  # decay factor

t_pred = math.log(alpha_a / alpha_b) / math.log(alpha_c)
print(t_pred)
```

## 4. Key Takeaway

The log model comes from basic physics.  It’s most suitable for systems that “coast” into the setpoint.
