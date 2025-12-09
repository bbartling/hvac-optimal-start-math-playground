# Day 50 — The Full Custom Engine

**Goal:** The Final Boss. Combine all previous lessons into a single Python script that acts as a custom Machine Learning Optimal Start Controller.

## 1. The Challenge

We will build a "Model 5" engine from scratch using only `numpy`. It will learn the physics of your building *and* the specific penalty of the weekend cold soak, without being explicitly programmed with an `IF` statement.

**The Mission:**
1.  **Input:** 20 days of training data (mixed Mondays and Weekdays).
2.  **Prep:** Normalize $\Delta T$ and encode the Monday Flag.
3.  **Train:** Run 5,000 epochs of Gradient Descent to find the perfect weights.
4.  **Predict:** Ask the model "How long for a 10°F warm-up on a Tuesday?" vs "How long on a Monday?"

## 2. The Code

```python
import numpy as np

# ==========================================
# PART 1: THE DATA (Messy Real World)
# ==========================================
# Format: [DeltaT (deg), Is_Monday (0/1), Actual_Minutes]
# Note: Mondays (1.0) take longer for the same temp!
raw_data = [
    [10.0, 0.0, 40.0],  # Tue: 10 deg -> 40 min
    [10.0, 1.0, 70.0],  # Mon: 10 deg -> 70 min (The Cold Soak!)
    [5.0,  0.0, 20.0],
    [5.0,  1.0, 50.0],  # Mon: 5 deg -> 50 min
    [2.0,  0.0, 8.0],
    [12.0, 1.0, 85.0],  # Cold Monday
    [8.0,  0.0, 32.0],
    [8.0,  1.0, 62.0],  # Similar temp, longer time
    [15.0, 0.0, 60.0],
    [3.0,  0.0, 12.0]
]

# Separate Inputs (X) and Targets (y)
X_raw = np.array([row[:2] for row in raw_data])
y = np.array([row[2] for row in raw_data])

# ==========================================
# PART 2: FEATURE ENGINEERING (Day 47)
# ==========================================
# Normalize DeltaT to be between 0 and 1
max_dT = 20.0 # Design day max
X = X_raw.copy()
X[:, 0] = X[:, 0] / max_dT 

# Add a "Bias" column of 1s (to learn the fixed intercept)
# X becomes: [Scaled_DeltaT, Is_Monday, 1.0]
X = np.c_[X, np.ones(len(X))]

# ==========================================
# PART 3: INITIALIZATION (Day 43)
# ==========================================
# Three weights: [Temp_Weight, Monday_Penalty, Fixed_Bias]
weights = np.random.rand(3) 
learning_rate = 0.05
epochs = 5000

print(f"Initial Random Weights: {weights}")

# ==========================================
# PART 4: THE TRAINING LOOP (Day 48)
# ==========================================
for epoch in range(epochs):
    # 1. Forward Pass (Prediction)
    y_pred = X.dot(weights)
    
    # 2. Calculate Error
    error = y_pred - y
    
    # 3. Calculate Gradient (Day 45)
    # The "Nudge" direction = average(error * input)
    gradient = (2/len(X)) * X.T.dot(error)
    
    # 4. Update Weights (Day 46)
    weights = weights - (learning_rate * gradient)
    
    # Optional: Watch it learn
    if epoch % 1000 == 0:
        mse = np.mean(error ** 2)
        print(f"Epoch {epoch}: Cost(MSE) = {mse:.4f}")

# ==========================================
# PART 5: THE RESULTS (Day 49)
# ==========================================
print("-" * 30)
print("TRAINING COMPLETE.")
print(f"Learned Weights: {weights}")
print("-" * 30)

# Interpreting the Brain
w_temp   = weights[0]
w_monday = weights[1]
w_bias   = weights[2]

print(f" > Base Rate (mins per normalized deg): {w_temp:.2f}")
print(f" > MONDAY PENALTY (mins):             {w_monday:.2f}")
print(f" > Fixed Overhead (mins):             {w_bias:.2f}")

# ==========================================
# PART 6: PREDICTION TEST
# ==========================================
print("-" * 30)
test_dT = 10.0
scaled_test = test_dT / max_dT

# Predict TUESDAY (Monday_Flag = 0)
input_tue = np.array([scaled_test, 0.0, 1.0])
pred_tue = input_tue.dot(weights)

# Predict MONDAY (Monday_Flag = 1)
input_mon = np.array([scaled_test, 1.0, 1.0])
pred_mon = input_mon.dot(weights)

print(f"SCENARIO: 10°F Warm-up")
print(f"Tuesday Prediction: {pred_tue:.1f} min")
print(f"Monday Prediction:  {pred_mon:.1f} min")
print(f"Difference:        +{pred_mon - pred_tue:.1f} min")
```

## 3. Final Reflection

Look at the **Monday Prediction**. The model automatically added roughly **30 minutes** (the exact difference in our training data) because it "saw" the pattern.

You have gone from calculating simple averages (Day 1) to building a gradient-descent learning engine (Day 50). You have successfully bridged the gap between traditional HVAC control and modern Artificial Intelligence.

## 4. Key Takeaway

You don't need a black-box cloud service to use AI in HVAC. With a little math and 50 days of practice, you can build self-learning logic that outperforms any static PID loop.

Here is that section formatted as **Part 5**, ready to be appended to the end of your Day 50 lesson plan.


## 5. The Future Path

Now that you have built the engine from scratch, you are ready to use the professional tools. You don't need to write `dw` and `db` by hand anymore.

### 1. SciKit-Learn (The Professional Standard)
In the real world, you replace the entire 50-line training loop with just two lines of code:
```python
from sklearn.linear_model import SGDRegressor

model = SGDRegressor()
model.fit(X, y)  # This runs the loop for you!
```

### 2. PyTorch / TensorFlow (The Deep End)

When building massive AI, you replace the manual gradient math (`dw`, `db`) with "Autograd"—automatic calculus engines:

```python
loss.backward()   # Automatically calculates all gradients
optimizer.step()  # Automatically updates all weights
```

### 3. Deep Learning (Neural Networks)

Once you have this structure, you can add a **"Hidden Layer"** (non-linearity) between your inputs and outputs.

  * **Current Model:** A straight line (Linear Regression).
  * **Neural Network:** A flexible curve that can bend and twist.
  * **The Benefit:** It allows the model to learn complex physics (like Model 1's curve or Model 4's decay) *automatically*, without you ever telling it to use `x squared` or `log`.

