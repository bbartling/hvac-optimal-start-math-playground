# Day 32 — The “Coast to Stop” Effect

**Goal:** Explain why Model 4 is useful for systems that slow down as they approach setpoint and illustrate the concept with examples and code.

## 1.  Why Heating Slows Down

Many HVAC systems warm up quickly at first when the temperature difference is large, but as they get close to the setpoint the rate of change slows dramatically.  This is similar to a car coasting into a parking spot.  Fans and coils have less “driving force” as the zone temperature rises.

Models 0–3 don’t explicitly capture this slowdown.  **Model 4** does by assuming the error decays exponentially:

```
error(t) = error(0) * (alpha_c)**t
```

where `0 < alpha_c < 1` is the decay factor from Day 31.

## 2.  Visualising the Coast

Let’s compute how the error shrinks over 10 minutes for two different decay factors:

```python
import math

def simulate_error(initial_error, alpha_c, minutes):
    return [initial_error * (alpha_c**t) for t in range(minutes+1)]

err_fast = simulate_error(10, 0.5, 10)  # faster decay
err_slow = simulate_error(10, 0.8, 10)  # slower decay
for t, (e1, e2) in enumerate(zip(err_fast, err_slow)):
    print(f"minute {t}: fast={e1:.2f}, slow={e2:.2f}")
```

You’ll see the “fast” system drops error quickly at first but still slows down near zero.  The “slow” system maintains a noticeable error much longer.

## 3.  Micro‑Exercises

1. Run the code above with your own `alpha_c` values (e.g., 0.6, 0.9) and plot the error over time.  
2. Compare the shape of the exponential decay to a quadratic warm‑up model for the same initial ΔT.  Which one spends more time close to the setpoint?  
3. Describe in words why a “coasting” effect can actually save energy in buildings with oversized equipment.

## 4.  Key Takeaway

Exponential models naturally account for the slowing rate of change near setpoint.  They are powerful when your building “coasts” the last few degrees.
