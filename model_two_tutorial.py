# ---------------------------------------------------------
# MODEL 2: RATIO ADJUSTMENT
# ---------------------------------------------------------

# 1. MADE UP DATA (History of the last 5 days)
# We need to know what the Outdoor Air Temp (OAT) was during those runs.
# Format: [Temp_Diff, Actual_Minutes, OAT_During_Run]
history = [
    [5.0, 25.0, 50.0],  # Day 1: 5 deg diff, took 25 min, 50F outside
    [3.0, 15.0, 55.0],  # Day 2: Warmer outside
    [8.0, 42.0, 30.0],  # Day 3: Cold! Long run.
    [4.0, 21.0, 48.0],  # Day 4
    [6.0, 30.0, 45.0]   # Day 5 (Yesterday)
]

# 2. SETTINGS
# Reference Temp: 100F for Cooling, 0F for Heating (We assume Heating here)
# This acts as an "anchor" for the ratio math.
T_ref = 0.0 

# We need to learn the "Base Rate" just like Model 0
learned_rate_sum = 0.0

print("--- STEP 1: LEARN BASE RATE ---")
for day in history:
    delta_t = day[0]
    minutes = day[1]
    
    # Simple Rate = Degrees / Minutes
    day_rate = delta_t / minutes
    learned_rate_sum += day_rate
    print(f"Day Rate: {day_rate:.3f} deg/min")

# Average the rates (Simple "Learning")
avg_base_rate = learned_rate_sum / len(history)
print(f"AVERAGE BASE RATE: {avg_base_rate:.3f} deg/min")


# 3. PREDICTION WITH WEATHER BUMP
print("\n--- STEP 2: PREDICT TOMORROW ---")

# Scenario: Tomorrow is 10 degrees from setpoint
tomorrow_delta_t = 10.0
# Scenario: Tomorrow is VERY COLD (20F) compared to Yesterday (45F)
tomorrow_oat = 20.0
yesterday_oat = history[-1][2] # Get the last item from history

# A. Normal Prediction (Model 0 style)
# Time = Degrees / Rate
base_minutes = tomorrow_delta_t / avg_base_rate
print(f"Base Prediction (No Weather): {base_minutes:.1f} minutes")

# B. Calculate the "Bump" Ratio
# PNNL Formula concept: (Ref - Yesterday) / (Ref - Today)
# If today is colder (closer to 0), the bottom number gets smaller, Ratio gets bigger.
ratio = (yesterday_oat - T_ref) / (tomorrow_oat - T_ref)
print(f"Weather Ratio: {ratio:.2f} (Because 20F is colder than 45F)")

# C. Apply Correction
final_minutes = base_minutes * ratio

print(f"FINAL PREDICTION: {final_minutes:.1f} minutes")