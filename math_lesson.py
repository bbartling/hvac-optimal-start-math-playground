



'''
Day 5 Micro-Exercise (You Solve This)

You have these warm-up datapoints:

| ΔT | x = ΔT² | t  |
| -- | ------- | -- |
| 4  | 16      | 26 |
| 6  | 36      | 44 |

Solve: t=ax+b


a = (82 - 40) / (64 - 25)
print(a)


# Solve for b | b = t1 ​− ax1​

b = 40 - a * 25
print(b)
'''



'''
Day 6 Micro-Exercise (You Solve This)

# Day 6 Micro-Exercise (Your turn)

# Zone temps (°F)
t_beginning = 62   # starting zone temperature
t_end = 72         # final zone temperature / setpoint

# Temperature rise (ΔT)
T = t_end - t_beginning  # Temp rise ΔT
print("Delta T (T) =", T)

# Warm-up time in minutes (actual observed warm-up time)
WUT = 72  # minutes

# Old model coefficients
a_old = 0.85
b_old = 12

# Smoothing factor
alpha = 0.12     # 12% weight to today's data

# Model 1 uses x = (ΔT)^2
x = T**2
print("x = T^2 =", x)

# Today's implied slope (a_today) from this single warm-up event
# t ≈ a * x  ->  a_today = t_actual / x
a_today = WUT / x
print("a_today (from today) =", a_today)

# Predicted warm-up using the old model
t_predicted = a_old * x + b_old
print("Algebraic t_predicted =", t_predicted)

# Self-tune the slope with EMA-style update
a_new = (1 - alpha) * a_old + alpha * a_today

# With only one datapoint, we usually don't change b
b_new = b_old  # keep intercept unchanged for a 1-point update

print("Algebraic a_new =", a_new)
print("Algebraic b_new =", b_new)

'''


