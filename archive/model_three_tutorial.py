"""
PNNL Model 3 – Multiple Regression Tutorial

This script shows:
  1) Made-up “history” of optimal start runs
  2) Fitting a Model 3-style regression:
         t = α3,d + α3,a * ΔT + α3,b * (ΔT * WF)
  3) Predicting minutes for a new day
  4) 3D visualization of the regression plane
"""

import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401


# ---------------------------------------------------------
# 1. MADE UP HISTORY (similar vibe to your Model 2 tutorial)
# Each record:
#   ΔT   = degrees from setpoint at start
#   WF   = weather factor (0–1), simplified proxy for OAT influence
#   mins = minutes it actually took to reach setpoint
# ---------------------------------------------------------
history = [
    {"dT": 3.0, "wf": 0.4, "mins": 20.0},
    {"dT": 5.0, "wf": 0.6, "mins": 35.0},
    {"dT": 7.0, "wf": 0.8, "mins": 50.0},
    {"dT": 2.0, "wf": 0.3, "mins": 15.0},
    {"dT": 6.0, "wf": 0.7, "mins": 40.0},
]

print("\n--- MODEL 3 HISTORY ---")
for i, row in enumerate(history, 1):
    print(
        f"Day {i}: "
        f"ΔT={row['dT']}°F, "
        f"WF={row['wf']}, "
        f"time={row['mins']} min"
    )
print()


# ---------------------------------------------------------
# 2. Build Regression Inputs
#
# Model 3-style form:
#
#   t = α3,d + α3,a * (ΔT) + α3,b * (ΔT * WF)
#
# where:
#   α3,d = baseline offset (minutes)
#   α3,a = sensitivity to ΔT
#   α3,b = extra influence of weather on ΔT
# ---------------------------------------------------------
dT = np.array([row["dT"] for row in history], dtype=float)
WF = np.array([row["wf"] for row in history], dtype=float)
mins = np.array([row["mins"] for row in history], dtype=float)

# Feature 1: ΔT
# Feature 2: ΔT * WF  (interaction term)
X = np.column_stack([dT, dT * WF])

# Fit Model 3 using scikit-learn
model = LinearRegression().fit(X, mins)

alpha_3_d = model.intercept_
alpha_3_a, alpha_3_b = model.coef_

print("--- MODEL 3 MULTIPLE REGRESSION RESULTS ---")
print(f"α3,d (baseline offset)           = {alpha_3_d:.3f}")
print(f"α3,a (ΔT influence)              = {alpha_3_a:.3f}")
print(f"α3,b (ΔT × WF influence)         = {alpha_3_b:.3f}")
print()


# ---------------------------------------------------------
# 3. Try a NEW DAY Prediction
# ---------------------------------------------------------
delta_t_today = 4.0   # 4°F away from setpoint at start
wf_today = 0.5        # medium weather factor

X_today = [[delta_t_today, delta_t_today * wf_today]]
t_pred = model.predict(X_today)[0]

print("--- MODEL 3 PREDICTION EXAMPLE ---")
print(f"Today's ΔT  = {delta_t_today}°F")
print(f"Today's WF  = {wf_today}")
print(f"Predicted Minutes to Setpoint = {t_pred:.1f} minutes\n")


# ---------------------------------------------------------
# 4. 3D VISUALIZATION: Regression Plane
#    X-axis: ΔT
#    Y-axis: WF
#    Z-axis: Predicted minutes
# ---------------------------------------------------------
dT_grid, WF_grid = np.meshgrid(
    np.linspace(dT.min(), dT.max(), 20),
    np.linspace(WF.min(), WF.max(), 20),
)

X_grid = np.column_stack([
    dT_grid.ravel(),
    (dT_grid * WF_grid).ravel()
])

mins_pred = model.predict(X_grid).reshape(dT_grid.shape)

fig = plt.figure()
ax = fig.add_subplot(111, projection="3d")

# Plot historical points
ax.scatter(dT, WF, mins, label="Historical Runs", s=60)

# Plot regression plane
ax.plot_surface(dT_grid, WF_grid, mins_pred, alpha=0.5)

ax.set_xlabel("ΔT (°F)")
ax.set_ylabel("WF (Weather Factor)")
ax.set_zlabel("Minutes to Setpoint")
ax.set_title("PNNL Model 3 — Multiple Regression Plane")

plt.legend()
plt.show()
