
import math
from typing import List

def mean(xs: List[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0

def clamp(x: float, lo: float, hi: float) -> float:
    return lo if x < lo else hi if x > hi else x

def ema(prev: float, new: float, w: float) -> float:
    # w in [0,1]
    return prev + w * (new - prev)

def safe_log(x: float, eps: float = 1e-9) -> float:
    return math.log(max(x, eps))

def estimate_c_least_squares(errors: List[float]) -> float:
    """c = sum(e_{i-1}*e_i)/sum(e_{i-1}^2)"""
    if len(errors) < 2:
        return 0.9
    num = 0.0
    den = 0.0
    for i in range(1, len(errors)):
        e_prev = errors[i - 1]
        e_cur = errors[i]
        num += e_prev * e_cur
        den += e_prev * e_prev
    return num / den if den else 0.9

def model4_topt_minutes(deadband_deg: float, e0: float, c: float) -> float:
    """t_opt = ln(a/b)/ln(c) with a=deadband, b=|e0|, 0<c<1."""
    a = max(deadband_deg, 1e-6)
    b = max(abs(e0), 1e-6)
    c = clamp(c, 1e-6, 0.999999)
    return safe_log(a / b) / safe_log(c)



deadband = 4.0
errors_yesterday = [6.0, 5.8, 4.2, 3.3, 2.5, 1.0, .33, .22, .11]  # yesterdays sampling during warmup
temp_delta_today = 7.2

c = estimate_c_least_squares(errors_yesterday)
t = model4_topt_minutes(deadband_deg=deadband, e0=temp_delta_today, c=c)

print("c:", c)
print("t_opt:", t, "minutes")



c_ema = 0.92
w = 0.30  # learning weight


for c_new in errors_yesterday:
    c_new = clamp(c_new, 0.80, 0.99)
    c_ema = ema(c_ema, c_new, w)
    print("c_ema:", round(c_ema, 4))