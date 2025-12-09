import math

# ---------------------------------------------------------
# MODEL 4: LOGARITHMIC DECAY
# ---------------------------------------------------------

# 1. MADE UP DATA
# We just need the temp diff and how long it took.
# Note: This model is VERY sensitive. If data is bad, math crashes.
history = [
    [5.0, 30.0],
    [10.0, 60.0],
    [2.0, 15.0],
    [8.0, 50.0],
    [4.0, 25.0]
]

# 2. SETTINGS
# The "Deadband" (alpha_a). This is how close to setpoint counts as "Done".
# We can't use 0.0 because log(0) is impossible.
deadband = 0.5 

print("--- STEP 1: LEARN DECAY RATE ---")
decay_rate_sum = 0.0

for day in history:
    start_diff = day[0]  # alpha_b
    minutes = day[1]     # t
    
    # We need to find 'alpha_c' (Decay Rate) for this day.
    # The PNNL formula rearranged:
    # alpha_c = exp( ln(deadband/start_diff) / minutes )
    
    # 1. Ratio of End / Start
    ratio = deadband / start_diff
    
    # 2. Natural Log of that ratio
    log_ratio = math.log(ratio)
    
    # 3. Divide by time to get the "per minute" log rate
    log_rate = log_ratio / minutes
    
    # 4. Exponentiate to get the decay factor (0 to 1)
    # A result of 0.95 means "we keep 95% of the error every minute"
    day_decay_rate = math.exp(log_rate)
    
    decay_rate_sum += day_decay_rate
    print(f"Day Decay Rate: {day_decay_rate:.4f}")

# Average the decay rates
avg_decay_rate = decay_rate_sum / len(history)
print(f"AVERAGE DECAY RATE: {avg_decay_rate:.4f}")


# 3. PREDICTION
print("\n--- STEP 2: PREDICT TOMORROW ---")
tomorrow_start_diff = 12.0 # Big gap to close

# The Formula: t = ln(deadband / start_diff) / ln(decay_rate)

numerator = math.log(deadband / tomorrow_start_diff)
denominator = math.log(avg_decay_rate)

pred_minutes = numerator / denominator

print(f"Prediction: {pred_minutes:.1f} minutes")