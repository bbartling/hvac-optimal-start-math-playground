"""
PNNL Model 3 – Manual Matrix Regression (Pure Python)
No NumPy, No SciKit-Learn. Just raw math for learning.
"""

# ---------------------------------------------------------
# 1. DATASET (Exact match to your tutorial)
# ---------------------------------------------------------
history = [
    {"dT": 3.0, "wf": 0.4, "mins": 20.0},
    {"dT": 5.0, "wf": 0.6, "mins": 35.0},
    {"dT": 7.0, "wf": 0.8, "mins": 50.0},
    {"dT": 2.0, "wf": 0.3, "mins": 15.0},
    {"dT": 6.0, "wf": 0.7, "mins": 40.0},
]

# ---------------------------------------------------------
# 2. CONSTRUCT DESIGN MATRIX X AND TARGET Y
# X = [Intercept(1), dT, dT*WF]
# ---------------------------------------------------------
X = []
Y = []
for row in history:
    X.append([1.0, row["dT"], row["dT"] * row["wf"]])
    Y.append(row["mins"])

def matrix_multiply_XT_X(X_mat):
    """Manually calculate X_Transpose * X (Result: 3x3)"""
    rows = len(X_mat)
    cols = len(X_mat[0])
    xtx = [[0.0] * cols for _ in range(cols)]
    for i in range(cols):
        for j in range(cols):
            for k in range(rows):
                xtx[i][j] += X_mat[k][i] * X_mat[k][j]
    return xtx

def matrix_multiply_XT_Y(X_mat, Y_vec):
    """Manually calculate X_Transpose * Y (Result: 3x1)"""
    rows = len(X_mat)
    cols = len(X_mat[0])
    xty = [0.0] * cols
    for i in range(cols):
        for k in range(rows):
            xty[i] += X_mat[k][i] * Y_vec[k]
    return xty

def determinant_3x3(m):
    """Calculate the determinant of a 3x3 matrix (Rule of Sarrus)"""
    return (m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1]) -
            m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0]) +
            m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]))

# ---------------------------------------------------------
# 3. SOLVE NORMAL EQUATION: (XT*X) * Beta = XT*Y
# ---------------------------------------------------------
xtx = matrix_multiply_XT_X(X)
xty = matrix_multiply_XT_Y(X, Y)

# Use Cramer's Rule to solve for Beta coefficients
det_main = determinant_3x3(xtx)

if abs(det_main) < 1e-9:
    print("Error: Singular Matrix")
else:
    beta = [0.0] * 3
    for i in range(3):
        # Create temporary matrix by replacing column i with xty
        temp_mat = [row[:] for row in xtx] # Deep copy
        for r in range(3):
            temp_mat[r][i] = xty[r]
        
        beta[i] = determinant_3x3(temp_mat) / det_main

    # ---------------------------------------------------------
    # 4. RESULTS (α3,d, α3,a, α3,b)
    # ---------------------------------------------------------
    print("--- MANUAL REGRESSION RESULTS ---")
    print(f"Alpha_3_d (Intercept): {beta[0]:.4f}")
    print(f"Alpha_3_a (dT):        {beta[1]:.4f}")
    print(f"Alpha_3_b (dT*WF):     {beta[2]:.4f}")

    # NEW DAY PREDICTION: Today's dT = 4.0, wf = 0.5
    dT_today = 4.0
    WF_today = 0.5
    prediction = beta[0] + (beta[1] * dT_today) + (beta[2] * (dT_today * WF_today))
    
    print(f"\nPrediction for 4°F, 0.5WF: {prediction:.4f} minutes")