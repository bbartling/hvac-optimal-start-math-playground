# ---------------------------------------------------------
# 1. MADE UP DATA (15 Days of History)
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

print("--- STEP 1: STATISTICS (Loop & Sum) ---")
print(f"Analyzing {len(history)} days of history...")

# Variables to hold our sums
sum_x = 0.0
sum_y = 0.0
sum_xy = 0.0
sum_x_squared = 0.0

# Loop through every single day (The "Statistics" part)
for day in history:
    delta_t = day[0]
    actual_minutes = day[1]

    # CRITICAL: For Quadratic Model 1, "x" is DeltaT SQUARED
    x = delta_t * delta_t 
    y = actual_minutes

    # Add to the piles
    sum_x += x
    sum_y += y
    sum_xy += (x * y)
    sum_x_squared += (x * x)

    # Optional: Print each day's math as we go
    # print(f"Day: dT={delta_t}, Mins={actual_minutes} --> x={x:.1f}, y={y}")

print("Sums calculated.")
print(f"Sum X: {sum_x:.1f}")
print(f"Sum Y: {sum_y:.1f}")

# ---------------------------------------------------------
# 2. REGRESSION (The Math Formula)
# Solving for y = ax + b (where x is deltaT^2)
# ---------------------------------------------------------
print("\n--- STEP 2: SOLVING THE REGRESSION ---")

n = len(history)
denominator = (n * sum_x_squared) - (sum_x * sum_x)

# Formula for Slope (alpha_a)
slope = ((n * sum_xy) - (sum_x * sum_y)) / denominator

# Formula for Intercept (alpha_b)
intercept = (sum_y - (slope * sum_x)) / n

print(f"LEARNED SLOPE (a):     {slope:.4f}")
print(f"LEARNED INTERCEPT (b): {intercept:.4f}")
print("-" * 30)
print(f"FINAL FORMULA: Minutes = {slope:.3f} * (DeltaT^2) + {intercept:.3f}")
print("-" * 30)

# ---------------------------------------------------------
# 3. PREDICTION (Using the new brain)
# ---------------------------------------------------------
print("\n--- STEP 3: PREDICTING TOMORROW ---")
tomorrow_delta_t = 10.0 # Let's say it's really cold tomorrow

# Apply the learned formula
pred_minutes = slope * (tomorrow_delta_t * tomorrow_delta_t) + intercept

print(f"Scenario: Tomorrow the zone is {tomorrow_delta_t} degrees from setpoint.")
print(f"Prediction: Start the unit {pred_minutes:.1f} minutes early.")