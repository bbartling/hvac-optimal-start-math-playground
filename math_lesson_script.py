# -----------------------------------------
# Day 13 — EMA smoothing of Model 1 coefficients
# Uses Day 12 regression outputs as "today's estimate"
# then applies EMA to produce stable coefficients.
# -----------------------------------------

def fit_model1_ols(data):
    """
    Fit Model 1: t = a*(ΔT²) + b using closed-form OLS.
    data: list of [deltaT, minutes]
    returns: (a, b, sse_fit, sse_mean)
    """
    n = float(len(data))
    if n < 2:
        raise Exception("Need at least 2 points")

    sum_x = 0.0       # x = ΔT²
    sum_y = 0.0
    sum_xy = 0.0
    sum_x2 = 0.0      # x²

    for deltaT, t in data:
        x = float(deltaT) ** 2
        y = float(t)
        sum_x += x
        sum_y += y
        sum_xy += x * y
        sum_x2 += x * x

    den = n * sum_x2 - (sum_x * sum_x)
    if abs(den) < 1e-9:
        raise Exception("Not enough variation in ΔT² (den ~ 0)")

    a = (n * sum_xy - sum_x * sum_y) / den
    b = (sum_y - a * sum_x) / n

    # SSE check (fitted vs baseline mean)
    mean_y = sum_y / n
    sse_fit = 0.0
    sse_mean = 0.0

    for deltaT, t in data:
        x = float(deltaT) ** 2
        actual = float(t)
        pred_fit = a * x + b
        sse_fit += (actual - pred_fit) ** 2
        sse_mean += (actual - mean_y) ** 2

    return a, b, sse_fit, sse_mean


# -----------------------------
# Day 12 demo dataset (single day)
# -----------------------------
data_day = [
    [1, 10],
    [3, 18],
    [5, 27],
    [7, 40],
    [12, 65],
]

a_today, b_today, sse_fit, sse_mean = fit_model1_ols(data_day)

print("\n--- Day 12 Regression (Today) ---")
print(f"Today a_new = {a_today:.6f}  [min/°F²]")
print(f"Today b_new = {b_today:.6f}  [min]")
print(f"SSE fitted = {sse_fit:.2f}, SSE mean = {sse_mean:.2f}")
print("✅ beats baseline" if sse_fit < sse_mean else "⚠️ does NOT beat baseline")


# -----------------------------------------
# Day 13 Micro-Exercise A:
# Simulate 5 days of (a_new, b_new) estimates
# and apply EMA with alpha = 0.2
# -----------------------------------------

alpha = 0.2

# Pretend these came from running regression each day
daily_estimates = [
    (1.10, 4.20),
    (1.35, 3.90),
    (1.05, 4.60),
    (1.50, 3.40),
    (1.25, 3.80),
]

# Initial EMA estimates (yesterday's tuned values)
a_est = 1.00
b_est = 4.00

print("\n--- Day 13 EMA Smoothing Over 5 Days ---")
print(f"EMA alpha = {alpha}")
print("day   a_new    a_est     b_new    b_est")
for i, (a_new, b_new) in enumerate(daily_estimates, start=1):
    a_est = a_est + alpha * (a_new - a_est)
    b_est = b_est + alpha * (b_new - b_est)
    print(f"{i:>3}  {a_new:>6.2f}  {a_est:>7.3f}   {b_new:>6.2f}  {b_est:>7.3f}")


