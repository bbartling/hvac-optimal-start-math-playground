



# Fit a simple multiple regression using NumPy
import numpy as np

# Sample data: each row is [ΔT, ΔT×WF]
X = np.array([[4, 4*0.7], [6, 6*0.6], [8, 8*0.8]])
y = np.array([30, 42, 70])

# Add a column of ones for the intercept
X_design = np.column_stack([X, np.ones(len(X))])

# Compute coefficients using the normal equation
coeffs = np.linalg.lstsq(X_design, y, rcond=None)[0]

alpha_a, alpha_b, alpha_d = coeffs
print(f"α₃,a = {alpha_a:.2f}")
print(f"α₃,b = {alpha_b:.2f}")
print(f"α₃,d = {alpha_d:.2f}")

print()
print(" ************************************** ")
print()

import numpy as np
from sklearn.linear_model import LinearRegression


# Fit regression
model = LinearRegression(fit_intercept=True)
model.fit(X, y)

a, b = model.coef_          # α3,a and α3,b (slopes)
d = model.intercept_        # α3,d (bias term)

print(f"α₃,a = {a:.2f}")
print(f"α₃,b = {b:.2f}")
print(f"α₃,d = {d:.2f}")