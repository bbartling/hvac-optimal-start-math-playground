import numpy as np

# ---------------------------------------------------------
# MODEL 5: THE GRADIENT DESCENT ENGINE (From Scratch)
# ---------------------------------------------------------
# CONCEPT:
# Instead of using algebra to "solve" for the answer, we will 
# use an iterative "Learning Loop" (Gradient Descent).
# This is exactly how Neural Networks (Deep Learning) work.
#
# FORMULA:
# Time = (w1 * DeltaT) + (w2 * Is_Monday) + Bias
# ---------------------------------------------------------

# 1. MADE UP DATA (20 Days)
# We artificially make Mondays take LONGER (Cold Soak effect).
# Format: [DeltaT (x1), Is_Monday_Flag (x2), Actual_Minutes (y)]
# Is_Monday_Flag: 0.0 = Tue-Fri, 1.0 = Monday
data = [
    # Week 1
    [10.0, 1.0, 60.0], # Monday: 10 deg takes 60 mins (Heavy!)
    [10.0, 0.0, 40.0], # Tuesday: 10 deg takes 40 mins (Normal)
    [5.0,  0.0, 20.0], # Wed
    [2.0,  0.0, 8.0],  # Thu
    [8.0,  0.0, 32.0], # Fri
    
    # Week 2
    [12.0, 1.0, 75.0], # Monday: Big load + Monday penalty
    [4.0,  0.0, 16.0], 
    [6.0,  0.0, 24.0],
    [9.0,  0.0, 36.0],
    [3.0,  0.0, 12.0],

    # Week 3
    [8.0,  1.0, 55.0], # Monday
    [7.0,  0.0, 28.0],
    [5.0,  0.0, 20.0],
    [11.0, 0.0, 44.0],
    [2.0,  0.0, 8.0],
    
    # Week 4 (Mixed)
    [10.5, 1.0, 65.0], # Cold Monday
    [6.5,  0.0, 26.0],
    [3.5,  0.0, 14.0],
    [9.5,  0.0, 38.0],
    [1.5,  0.0, 6.0]
]

# Convert to Numpy for easier math
# X = Inputs (DeltaT, IsMonday), y = Target (Minutes)
X_raw = np.array([row[:2] for row in data])
y = np.array([row[2] for row in data])

# ---------------------------------------------------------
# 2. PRE-PROCESSING (Normalization)
# ---------------------------------------------------------
# ML Engines learn faster if data is between 0 and 1.
# We divide DeltaT by the max value to "shrink" it.
max_dT = np.max(X_raw[:, 0])

X = X_raw.copy()
X[:, 0] = X[:, 0] / max_dT # Scale DeltaT to 0.0 - 1.0 range
# Note: Is_Monday is already 0 or 1, so it's fine.

print("--- STEP 1: INITIALIZE THE BRAIN ---")
# Randomly guess weights to start. 
# w1 (DeltaT weight), w2 (Monday Penalty weight)
weights = np.array([0.5, 0.5]) 
bias = 0.0 

learning_rate = 0.01  # How big of a step to take when learning
epochs = 2000         # How many times to "practice"

print(f"Starting Weights: {weights}")
print(f"Starting Bias:    {bias}")

# ---------------------------------------------------------
# 3. THE TRAINING LOOP (Gradient Descent)
# ---------------------------------------------------------
print("\n--- STEP 2: TRAINING (Iterative Learning) ---")

for epoch in range(epochs):
    
    # A. FORWARD PASS (Make a Prediction)
    # Prediction = (X * weights) + bias
    # np.dot does the multiplication and addition for us
    y_pred = np.dot(X, weights) + bias
    
    # B. CALCULATE ERROR (Loss)
    # How far off were we?
    error = y_pred - y
    
    # Calculate Mean Squared Error (just for us to watch)
    mse = np.mean(error ** 2)
    
    # C. BACKWARD PASS (Calculate Gradients)
    # This is the "Calculus" part. It tells us which direction to move.
    # Logic: If error is positive, we guessed too high -> lower the weights.
    
    # Gradient for Weights = average( error * Input_Value )
    dw = (2 / len(X)) * np.dot(X.T, error)
    
    # Gradient for Bias = average( error )
    db = (2 / len(X)) * np.sum(error)
    
    # D. UPDATE THE BRAIN (The Learning Step)
    weights = weights - (learning_rate * dw)
    bias    = bias    - (learning_rate * db)
    
    # Print progress every 500 epochs
    if epoch % 500 == 0:
        print(f"Epoch {epoch}: Loss (MSE) = {mse:.4f}")

print("-" * 30)
print(f"TRAINING COMPLETE.")
print(f"Final Loss: {mse:.4f}")
print(f"Learned Weights: {weights}") 
print(f"Learned Bias:    {bias:.4f}")
print("-" * 30)

# ---------------------------------------------------------
# 4. TESTING THE "MONDAY INTELLIGENCE"
# ---------------------------------------------------------
print("\n--- STEP 3: THE MONDAY SHOWDOWN ---")

# Let's see if it learned that Mondays are harder.
# Scenario: 10 Degrees Delta T
test_dT = 10.0
scaled_dT = test_dT / max_dT # Remember to scale it!

# CASE A: It is a TUESDAY (Is_Monday = 0)
inputs_tue = np.array([scaled_dT, 0.0])
pred_tue = np.dot(inputs_tue, weights) + bias

# CASE B: It is a MONDAY (Is_Monday = 1)
inputs_mon = np.array([scaled_dT, 1.0])
pred_mon = np.dot(inputs_mon, weights) + bias

print(f"Scenario: The building is {test_dT} degrees cold.")
print(f" > Prediction for TUESDAY: {pred_tue:.1f} minutes")
print(f" > Prediction for MONDAY:  {pred_mon:.1f} minutes")

diff = pred_mon - pred_tue
print(f"\nRESULT: The engine automatically added {diff:.1f} minutes because it's Monday!")

# ---------------------------------------------------------
# THE FUTURE PATH
# ---------------------------------------------------------
# 1. SciKit-Learn: 
#    You would replace the entire loop with:
#    model = SGDRegressor() 
#    model.fit(X, y)
#
# 2. PyTorch / TensorFlow: 
#    You would replace the manual gradient math (dw, db) with:
#    loss.backward()
#    optimizer.step()
#
# 3. Deep Learning: 
#    Once you have this structure, you can add a "Hidden Layer" (non-linearity) 
#    between the inputs and output. That turns this simple Regressor into a 
#    Neural Network, allowing it to learn complex curves without you telling 
#    it "x squared" (Model 1) or "log" (Model 4).