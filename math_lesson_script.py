# -----------------------------------------
# Day 12 — Model 1 (Quadratic-in-DeltaT) via OLS
# t = alpha_a * (DeltaT^2) + alpha_b
# -----------------------------------------

data = [
    [1, 10],
    [3, 18],
    [5, 27],
    [7, 40],
    [12, 65],
]

# 1) Build regression sums using x = (DeltaT^2)
n = float(len(data))

sum_x = 0.0         # Σx  where x = ΔT²
sum_y = 0.0         # Σy
sum_xy = 0.0        # Σxy
sum_x2 = 0.0        # Σx²  where x² = (ΔT²)² = ΔT⁴

print("ΔT  time(min)  x=ΔT²")
for deltaT, t in data:
    x = float(deltaT) * float(deltaT)  # ΔT²
    y = float(t)
    print(f"{deltaT:>2}  {t:>8}  {x:>5.1f}")

    sum_x += x
    sum_y += y
    sum_xy += x * y
    sum_x2 += x * x

# 2) Closed-form OLS coefficients for y = a*x + b
den = n * sum_x2 - (sum_x * sum_x)
if abs(den) < 1e-9:
    raise Exception("Not enough variation in ΔT² to fit Model 1 (denominator ~ 0).")

alpha_a = (n * sum_xy - sum_x * sum_y) / den
alpha_b = (sum_y - alpha_a * sum_x) / n

print("\n--- Learned Model 1 Coefficients ---")
print(f"alpha_1,a (slope on ΔT²) = {alpha_a:.6f}  [min / °F²]")
print(f"alpha_1,b (intercept)    = {alpha_b:.6f}  [min]")
print(f"Model: t = {alpha_a:.6f}*(ΔT²) + {alpha_b:.6f}")

# 3) Verify: compute SSE for fitted model and baseline mean model
mean_y = sum_y / n

sse_fit = 0.0
sse_mean = 0.0

print("\n--- Per-point Predictions & Errors ---")
print("ΔT   actual  pred_fit  err_fit   pred_mean  err_mean")
for deltaT, t in data:
    x = float(deltaT) * float(deltaT)
    actual = float(t)

    pred_fit = alpha_a * x + alpha_b
    err_fit = actual - pred_fit
    sse_fit += err_fit * err_fit

    pred_mean = mean_y
    err_mean = actual - pred_mean
    sse_mean += err_mean * err_mean

    print(f"{deltaT:>2}  {actual:>6.1f}  {pred_fit:>8.2f}  {err_fit:>7.2f}   {pred_mean:>8.2f}  {err_mean:>8.2f}")

print("\n--- SSE Comparison ---")
print(f"SSE (fitted Model 1) = {sse_fit:.2f}")
print(f"SSE (baseline mean)  = {sse_mean:.2f}")

if sse_fit < sse_mean:
    print("✅ Learned model beats the baseline mean (good).")
else:
    print("⚠️ Learned model does NOT beat the baseline mean (check data or model form).")

# 4) Tomorrow prediction using Model 1
tomorrows_space_temp = 60
occ_heat_stp = 72
deltaT_tomorrow = occ_heat_stp - tomorrows_space_temp

minutes_tomorrow = alpha_a * (deltaT_tomorrow ** 2) + alpha_b

print("\n--- Tomorrow Prediction ---")
print(f"Tomorrow ΔT = {deltaT_tomorrow:.2f} °F")
print(f"Predicted minutes = {minutes_tomorrow:.2f} min")
