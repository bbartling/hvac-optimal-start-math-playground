history = [
    [2.0, 10.0],  # Day 1: 2 degrees took 10 mins (Rate = 0.2 deg/min)
    [5.0, 25.0],  # Day 2: 5 degrees took 25 mins (Rate = 0.2 deg/min)
    [8.0, 40.0],  # Day 3: Rate = 0.2
    [3.0, 15.0],  # Day 4: Rate = 0.2
    [6.0, 29.0],  # Day 5: Rate = 0.206 (A little faster)
    [10.0, 50.0], # Day 6: Rate = 0.2
    [4.0, 19.0],  # Day 7: Rate = 0.21
    [5.5, 27.0],  # Day 8: Rate = 0.203
    [9.0, 45.0],  # Day 9: Rate = 0.2
    [2.5, 12.0],  # Day 10: Rate = 0.208
    [7.0, 36.0],  # Day 11: Rate = 0.194 (A little slower)
    [6.5, 32.0],  # Day 12: Rate = 0.203
    [3.5, 17.0],  # Day 13: Rate = 0.205
    [8.5, 42.0],  # Day 14: Rate = 0.202
    [4.5, 22.0]   # Day 15: Rate = 0.204
]
# -----------------------------
# Regression step (physics)
# Model 1: t = a * (ΔT²) + b
# -----------------------------

n = len(history)

sum_x = 0.0        # Σ(ΔT²)
sum_y = 0.0        # Σ(t)
sum_xy = 0.0       # Σ(ΔT² · t)
sum_x2 = 0.0       # Σ((ΔT²)²) = Σ(ΔT⁴)

for record in history:
    deltaT = record[0]
    time = record[1]

    x = deltaT * deltaT   # ΔT²
    y = time

    sum_x += x
    sum_y += y
    sum_xy += x * y
    sum_x2 += x * x

# ---- THE IMPORTANT PART ----
denominator = n * sum_x2 - (sum_x * sum_x)

if abs(denominator) < 1e-9:
    raise Exception("Not enough variation in ΔT² to fit Model 1")

# Solve for regression coefficients
a_new = (n * sum_xy - sum_x * sum_y) / denominator
b_new = (sum_y - a_new * sum_x) / n

print(f"Regression result: t = {a_new:.3f}*(ΔT²) + {b_new:.3f}")

# -----------------------------
# EMA step (trust)
# -----------------------------

alpha = 0.2

# Yesterday’s trusted values
a_est = 1.0
b_est = 4.0

# Blend today’s regression into trust
a_est = a_est + alpha * (a_new - a_est)
b_est = b_est + alpha * (b_new - b_est)

print(f"EMA-smoothed: a={a_est:.3f}, b={b_est:.3f}")


print("\n PREDICTING TOMORROW ---")
tomorrow_delta_t = 10.0 # Cold morning!

# alpha a = minutes / °F² and alpha b = minutes
pred_minutes = a_new * (tomorrow_delta_t ** 2) + b_new
print(f"Scenario: Tomorrow the zone is {tomorrow_delta_t} degrees from setpoint.")
print(f"Prediction: Start the unit {pred_minutes:.1f} minutes early.")


