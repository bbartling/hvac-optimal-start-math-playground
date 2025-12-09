import numpy as np

# ---------------------------------------------------------
# MODEL 3: MULTIPLE REGRESSION (Matrix Math)
# ---------------------------------------------------------

# 1. MADE UP DATA
# We calculate "Weather Factor" (WF) before putting it in the list.
# WF is usually (Setpoint - OAT). Bigger WF = Colder outside.
# Format: [Delta_T (x1), Weather_Factor (x2), Actual_Minutes (y)]
history = [
    [2.0,  10.0,  12.0],  # Mild day
    [5.0,  20.0,  30.0],  # Colder
    [8.0,  40.0,  55.0],  # Very Cold
    [3.0,  15.0,  18.0],
    [6.0,  25.0,  38.0],
    [10.0, 50.0,  70.0],  # Deep freeze!
    # ... pretend we have 15 days ...
    [4.0,  18.0,  25.0],
    [5.5,  22.0,  33.0],
    [9.0,  45.0,  62.0],
    [2.5,  12.0,  14.0],
    [7.0,  30.0,  48.0],
    [6.5,  28.0,  42.0],
    [3.5,  16.0,  20.0],
    [8.5,  42.0,  58.0],
    [4.5,  19.0,  28.0]
]

print("--- STEP 1: PREPARE MATRICES ---")

# We need two lists for the solver:
# Matrix 'A' (The Inputs): [DeltaT, WeatherFactor, 1.0]
# Vector 'B' (The Answers): [ActualMinutes]
matrix_A = []
vector_B = []

for day in history:
    dT = day[0]
    WF = day[1]
    minutes = day[2]

    # The row must correspond to [x1, x2, Intercept_Helper]
    # We add 1.0 so the math can find the "d" (intercept) value
    row = [dT, WF, 1.0]
    
    matrix_A.append(row)
    vector_B.append(minutes)

# Convert to Numpy Arrays (The solver needs these specific formats)
np_A = np.array(matrix_A)
np_B = np.array(vector_B)

print("Matrices ready.")
# print("A looks like:\n", np_A) # Uncomment to see the grid

# ---------------------------------------------------------
# 2. SOLVE (The Magic Step)
# This one line replaces pages of algebra.
# It finds the "Least Squares" best fit for a, b, and d.
# ---------------------------------------------------------
print("\n--- STEP 2: SOLVING... ---")

# We use 'lstsq' (Least Squares) because real data is messy and 
# 'solve' only works if data is 100% perfect.
# rcond=None just tells it to ignore tiny errors.
solution = np.linalg.lstsq(np_A, np_B, rcond=None)[0]

a = solution[0] # Coefficient for Delta T
b = solution[1] # Coefficient for Weather Factor
d = solution[2] # The Intercept (Baseline overhead)

print(f"SOLVED COEFFICIENTS:")
print(f"a (DeltaT impact): {a:.4f}")
print(f"b (Weather impact): {b:.4f}")
print(f"d (Fixed Overhead): {d:.4f}")

# ---------------------------------------------------------
# 3. PREDICTION
# ---------------------------------------------------------
print("\n--- STEP 3: PREDICT TOMORROW ---")
# Tomorrow: 10 degree difference, Weather Factor 50 (Very Cold)
tom_dT = 10.0
tom_WF = 50.0

# The Formula: t = a*dT + b*WF + d
pred_minutes = (a * tom_dT) + (b * tom_WF) + d

print(f"Prediction: {pred_minutes:.1f} minutes")