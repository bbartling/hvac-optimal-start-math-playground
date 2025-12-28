# ---------------------------------------------------------
# 1. MADE UP DATA (15 Days of History)
# Format: {"delta_t": °F from setpoint, "minutes": warmup time, "oat": °F}
# ---------------------------------------------------------
history = [
    {"delta_t": 2.0, "minutes": 10.0, "oat": 35.0},
    {"delta_t": 5.0, "minutes": 25.0, "oat": 34.0},
    {"delta_t": 8.0, "minutes": 40.0, "oat": 33.0},
    {"delta_t": 3.0, "minutes": 15.0, "oat": 32.0},
    {"delta_t": 6.0, "minutes": 29.0, "oat": 30.0},
    {"delta_t": 10.0, "minutes": 50.0, "oat": 28.0},
    {"delta_t": 4.0, "minutes": 19.0, "oat": 27.0},
    {"delta_t": 5.5, "minutes": 27.0, "oat": 25.0},
    {"delta_t": 9.0, "minutes": 45.0, "oat": 24.0},
    {"delta_t": 2.5, "minutes": 12.0, "oat": 22.0},
    {"delta_t": 7.0, "minutes": 36.0, "oat": 20.0},
    {"delta_t": 6.5, "minutes": 32.0, "oat": 18.0},
    {"delta_t": 3.5, "minutes": 17.0, "oat": 15.0},
    {"delta_t": 8.5, "minutes": 42.0, "oat": 10.0},
    {"delta_t": 4.5, "minutes": 22.0, "oat": 5.0},  # Day 15 (yesterday)
]

print("--- HISTORY (last few days) ---")

last_five = history[-5:]
day_index = len(history) - 4  # starting day number

for row in last_five:
    print(
        f"Day {day_index}: dT={row['delta_t']}°F, "
        f"time={row['minutes']} min, "
        f"OAT={row['oat']}°F"
    )
    day_index += 1

print()


# ---------------------------------------------------------
# 2. MODEL 1 PREDICTION (NO WEATHER)
# t = a * (ΔT²) + b
# ---------------------------------------------------------
delta_t = 6.0
alpha1_a, alpha1_b = 1.0, 4.0

t_model1 = alpha1_a * (delta_t**2) + alpha1_b

print("--- MODEL 1 (no weather) ---")
print(f"Today ΔT = {delta_t:.1f}°F from setpoint.")
print(f"Model 1 prediction: {t_model1:.1f} minutes of warmup.\n")

# ---------------------------------------------------------
# 3. MODEL 2 BASE TIME (LINEAR RATE FROM YESTERDAY)
# α2,a = ΔT_yesterday / time_yesterday   (°F per minute)
# t_base = ΔT_today / α2,a               (minutes)
# ---------------------------------------------------------
yesterday = history[-1]  # last record
dt_y = yesterday["delta_t"]
t_y = yesterday["minutes"]
oat_y = yesterday["oat"]

alpha2a = dt_y / t_y  # °F per minute

t_base = delta_t / alpha2a

print("--- MODEL 2 BASE TIME (no OAT yet) ---")
print(f"Yesterday: dT={dt_y:.1f}°F, time={t_y:.1f} min, OAT={oat_y:.1f}°F")
print(f"Learned α2,a = {alpha2a:.3f} °F/min")
print(f"Today dT = {delta_t:.1f}°F → base time (no weather) = {t_base:.1f} min\n")

# ---------------------------------------------------------
# 4. MODEL 2 WITH OAT RATIO (PAPER STYLE)
# ratio = (T_ref - OAT_yesterday) / (T_ref - OAT_today)
# t_model2 = t_base * ratio
# ---------------------------------------------------------
T_ref = 32.0  # Heating reference from paper
oat_yesterday = 28.0
oat_today = 20.0  # Colder morning

ratio = (T_ref - oat_yesterday) / (T_ref - oat_today)
t_model2 = t_base * ratio

print("--- MODEL 2 (single example with OAT ratio) ---")
print(f"T_ref        = {T_ref:.1f}°F")
print(f"OAT_yesterday = {oat_yesterday:.1f}°F")
print(f"OAT_today     = {oat_today:.1f}°F  (colder)")
print(f"Ratio = (T_ref - OAT_y) / (T_ref - OAT_t) = {ratio:.3f}")
print(f"Model 2 prediction: {t_model2:.1f} minutes of warmup.\n")

print("Compare:")
print(f"  Model 1 (no weather): {t_model1:.1f} minutes")
print(f"  Model 2 (with ratio): {t_model2:.1f} minutes\n")

# ---------------------------------------------------------
# 5. RATIO SENSITIVITY (HEATING MODE)
# Sweep OAT_today and see how the ratio changes.
# ---------------------------------------------------------
print("--- MODEL 2 HEATING RATIO SENSITIVITY ---")
T_ref = 32.0
oat_prev = 25.0  # fixed "yesterday" OAT

print(f"T_ref = {T_ref:.1f}°F, OAT_yesterday = {oat_prev:.1f}°F\n")

for oat_curr in [15.0, 20.0, 25.0, 30.0]:
    ratio = (T_ref - oat_prev) / (T_ref - oat_curr)
    t_opt = t_base * ratio
    print(f"Today OAT={oat_curr:5.1f}°F → ratio={ratio:6.2f}, t_opt={t_opt:6.1f} min")

print("\nNote:")
print("- This is the raw Model 2 ratio from the paper.")
print("- It shows how OAT_today changes the final minutes.")
print("- In real BAS code we usually clamp or tweak this ratio")
print("  so colder mornings always mean more runtime.")
