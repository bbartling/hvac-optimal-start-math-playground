# ---------------------------------------------------------
# 1. MADE UP DATA (15 Days of History)
# Format: [Temp_Diff_Degrees, Actual_Minutes_To_Recover]
# ---------------------------------------------------------
history = [
    [2.0, 10.0],  # Day 1: 2 degrees took 10 mins (Rate = 0.2 deg/min)
    [5.0, 25.0],  # Day 2: 5 degrees took 25 mins (Rate = 0.2 deg/min)
    [8.0, 40.0],  # Day 3: Rate = 0.2
    [3.0, 15.0],  # Day 4: Rate = 0.2
    [6.0, 29.0],  # Day 5: Rate = 0.206 (A little faster)
    [10.0, 50.0],  # Day 6: Rate = 0.2
    [4.0, 19.0],  # Day 7: Rate = 0.21
    [5.5, 27.0],  # Day 8: Rate = 0.203
    [9.0, 45.0],  # Day 9: Rate = 0.2
    [2.5, 12.0],  # Day 10: Rate = 0.208
    [7.0, 36.0],  # Day 11: Rate = 0.194 (A little slower)
    [6.5, 32.0],  # Day 12: Rate = 0.203
    [3.5, 17.0],  # Day 13: Rate = 0.205
    [8.5, 42.0],  # Day 14: Rate = 0.202
    [4.5, 22.0],  # Day 15: Rate = 0.204
]

# ---------------------------------------------------------
# 2. INITIALIZE THE "BRAIN"
# ---------------------------------------------------------
# We start with a default guess, just like the Java code
current_learned_rate = 0.1  # Default: 0.1 degrees per minute
ema_weight = 0.2  # The "Smoothing Factor" (Alpha)

print(f"--- STARTING ---")
print(f"Initial Learned Rate: {current_learned_rate:.3f} deg/min")
print("-" * 30)

# ---------------------------------------------------------
# 3. THE "LEARNING LOOP" (EMA Logic)
# ---------------------------------------------------------
day_count = 1

for day in history:
    delta_t = day[0]
    actual_minutes = day[1]

    # Step A: Calculate today's raw performance
    # Formula: Rate = Degrees / Minutes
    today_rate = delta_t / actual_minutes

    # Step B: Update the Running Average (EMA)
    # Formula: New = Old + Weight * (Today - Old)
    # This is exactly how the Java code updates 'degreesPerMinuteHeat'
    previous_rate = current_learned_rate
    current_learned_rate = previous_rate + ema_weight * (today_rate - previous_rate)

    print(f"Day {day_count}: dT={delta_t}, Time={actual_minutes}m")
    print(f"   -> Today's Raw Rate: {today_rate:.3f}")
    print(f"   -> UPDATED Learned Rate: {current_learned_rate:.3f}")

    day_count += 1

print("-" * 30)
print(f"FINAL LEARNED RATE: {current_learned_rate:.4f} deg/min")
print("-" * 30)

# ---------------------------------------------------------
# 4. PREDICTION (Using the Linear Brain)
# ---------------------------------------------------------
print("\n--- STEP 3: PREDICTING TOMORROW ---")
tomorrow_delta_t = 10.0  # Cold morning!

# Formula: Minutes = Degrees / Rate
pred_minutes = tomorrow_delta_t / current_learned_rate

print(f"Scenario: Tomorrow the zone is {tomorrow_delta_t} degrees from setpoint.")
print(f"Prediction: Start the unit {pred_minutes:.1f} minutes early.")
