import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401


# ---------------------------------------------------------
# 1. MADE UP HISTORY (similar vibe to your Model 2 tutorial)
# Each record:
#   ΔT  = degrees from setpoint at start
#   WF  = weather factor (0–1), simplified proxy for OAT influence
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
        f"dT={row['dT']}°F, "
        f"WF={row['wf']}, "
        f"time={row['mins']} min"
    )
print()


# ---------------------------------------------------------
# 2. Build Regression Inputs
# Model form:
#
#   t = α0 + α1(ΔT) + α2(WF)
#
# ---------------------------------------------------------
dT  = np.array([row["dT"] for row in history], dtype=float)
WF  = np.array([row["wf"] for row in history], dtype=float)
mins = np.array([row["mins"] for row in history], dtype=float)

# Stack inputs into feature matrix
X = np.column_stack([dT, WF])

# Fit Model 3
model = LinearRegression().fit(X, mins)

alpha0 = model.intercept_
alpha1, alpha2 = model.coef_

print("--- MODEL 3 MULTIPLE REGRESSION RESULTS ---")
print(f"α0 (intercept)        = {alpha0:.3f}")
print(f"α1 (ΔT coefficient)    = {alpha1:.3f}")
print(f"α2 (WF coefficient)    = {alpha2:.3f}")
print()


# ---------------------------------------------------------
# 3. Try a NEW DAY Prediction
# ---------------------------------------------------------
delta_t_today = 4.0
wf_today = 0.5

t_pred = model.predict([[delta_t_today, wf_today]])[0]

print("--- MODEL 3 PREDICTION EXAMPLE ---")
print(f"Today's ΔT  = {delta_t_today}°F")
print(f"Today's WF  = {wf_today}")
print(f"Predicted Minutes to Setpoint = {t_pred:.1f} minutes\n")


# ---------------------------------------------------------
# 4. 3D VISUALIZATION: Regression Plane
# ---------------------------------------------------------
dT_grid, WF_grid = np.meshgrid(
    np.linspace(dT.min(), dT.max(), 20),
    np.linspace(WF.min(), WF.max(), 20)
)

X_grid = np.column_stack([dT_grid.ravel(), WF_grid.ravel()])
mins_pred = model.predict(X_grid).reshape(dT_grid.shape)

fig = plt.figure()
ax = fig.add_subplot(111, projection="3d")

# Plot historical points
ax.scatter(dT, WF, mins, color="blue", label="Historical Runs", s=60)

# Plot regression plane
ax.plot_surface(dT_grid, WF_grid, mins_pred, alpha=0.5, color="orange")

ax.set_xlabel("ΔT (°F)")
ax.set_ylabel("WF (Weather Factor)")
ax.set_zlabel("Minutes to Setpoint")
ax.set_title("PNNL Model 3 — Multiple Regression Plane")

plt.legend()
plt.show()
