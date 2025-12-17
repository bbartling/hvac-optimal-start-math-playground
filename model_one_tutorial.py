# ---------------------------------------------------------
# 1) MADE UP DATA (15 Days of History)
# Format: [Temp_Diff_Degrees, Actual_Minutes_To_Recover]
# ---------------------------------------------------------
history = [
    [2.0, 6.0],   # Day 1: Small diff, short run
    [5.0, 8.5],   # Day 2: Medium diff
    [8.0, 12.0],  # Day 3: Big diff, longer run
    [3.0, 6.5],
    [6.0, 9.0],
    [10.0, 16.0], # Day 6: Very cold morning!
    [4.0, 7.0],
    [5.5, 8.8],
    [9.0, 14.0],
    [2.5, 6.2],
    [7.0, 10.5],
    [6.5, 9.8],
    [3.5, 6.8],
    [8.5, 13.0],
    [4.5, 7.5]    # Day 15
]

# Defaults (same spirit as your Niagara block)
DEFAULT_A = 0.10
DEFAULT_B = 5.00

# EMA smoothing factor for coefficient updates (Day 13 behavior)
EMA_ALPHA = 0.2


# ---------------------------------------------------------
# Helper: compute regression for Model 1 on a window of history
# Returns (a, b) for: minutes = a*(ΔT^2) + b
# ---------------------------------------------------------
def compute_model1_regression(window):
    """
    Ordinary Least Squares for y = a*x + b with:
      x = (ΔT^2)
      y = minutes

    Returns:
      (a, b)
    """
    n = len(window)
    if n < 2:
        return DEFAULT_A, DEFAULT_B

    sum_x = 0.0
    sum_y = 0.0
    sum_xy = 0.0
    sum_x2 = 0.0

    for delta_t, minutes in window:
        x = delta_t * delta_t
        y = minutes
        sum_x += x
        sum_y += y
        sum_xy += x * y
        sum_x2 += x * x

    denom = (n * sum_x2) - (sum_x * sum_x)
    if abs(denom) < 1e-9:
        return DEFAULT_A, DEFAULT_B

    a = ((n * sum_xy) - (sum_x * sum_y)) / denom
    b = (sum_y - (a * sum_x)) / n

    # Basic safety clamps (match your Java philosophy)
    if a < 0:
        a = DEFAULT_A
    if b < 0:
        b = 0.0

    return a, b


# ---------------------------------------------------------
# 2) REGRESSION on the full dataset (the "learned brain")
# ---------------------------------------------------------
print("--- STEP 1/2: LEARN MODEL 1 FROM HISTORY ---")
a_full, b_full = compute_model1_regression(history)
print(f"Learned a (slope):     {a_full:.4f}")
print(f"Learned b (intercept): {b_full:.2f}")
print(f"FINAL FORMULA: Minutes = {a_full:.4f} * (DeltaT^2) + {b_full:.2f}")


# ---------------------------------------------------------
# 3) PREDICT TOMORROW (using the learned brain)
# ---------------------------------------------------------
print("\n--- STEP 3: PREDICTING TOMORROW ---")
tomorrow_delta_t = 10.0  # example: 10°F away from setpoint
pred_minutes = a_full * (tomorrow_delta_t * tomorrow_delta_t) + b_full
print(f"Scenario: Tomorrow ΔT = {tomorrow_delta_t:.1f}°F")
print(f"Prediction: Start {pred_minutes:.1f} minutes early.")


# ---------------------------------------------------------
# 4) SELF-TUNING (EMA on coefficients)  <-- key addition
# ---------------------------------------------------------
print("\n--- STEP 4: SELF-TUNING WITH EMA (COEFFICIENTS) ---")
a_est = DEFAULT_A
b_est = DEFAULT_B
print(f"Starting estimates: a_est={a_est:.4f}, b_est={b_est:.2f}, EMA_ALPHA={EMA_ALPHA}")

# "Daily" updates by expanding history:
# Day 2 uses history[0:2], Day 3 uses history[0:3], ...
for day_end in range(2, len(history) + 1):
    window = history[:day_end]
    a_new, b_new = compute_model1_regression(window)

    # EMA blend (matches your Java block approach)
    a_est = a_est + EMA_ALPHA * (a_new - a_est)
    b_est = b_est + EMA_ALPHA * (b_new - b_est)

    print(
        f"Day {day_end:>2}: a_new={a_new:.4f}, b_new={b_new:.2f}"
        f"  -->  a_est={a_est:.4f}, b_est={b_est:.2f}"
    )

print("\nFINAL TUNED MODEL (after EMA):")
print(f"Minutes = {a_est:.4f} * (DeltaT^2) + {b_est:.2f}")

pred_minutes_ema = a_est * (tomorrow_delta_t * tomorrow_delta_t) + b_est
print(f"For ΔT={tomorrow_delta_t:.1f}°F, EMA-tuned predicts: {pred_minutes_ema:.1f} minutes")


# ---------------------------------------------------------
# 5) OPTIONAL: show error on the *last* day like your Niagara slots
# ---------------------------------------------------------
print("\n--- STEP 5 (OPTIONAL): LAST-RUN ERROR DEMO ---")
last_day_delta_t, last_day_actual = history[-1]
last_day_pred = a_est * (last_day_delta_t * last_day_delta_t) + b_est
last_day_error = last_day_pred - last_day_actual  # positive = overpredicted
print(f"Last day: ΔT={last_day_delta_t:.1f}, actual={last_day_actual:.1f}")
print(f"Predicted={last_day_pred:.1f}  Error(pred-actual)={last_day_error:+.1f} minutes")
