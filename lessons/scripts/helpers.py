"""
Tiny math helpers (no NumPy).
Used across the bonus week scripts.
"""
from __future__ import annotations
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

def simulate_first_order_errors(
    e0: float,
    c: float,
    steps: int,
    noise: float = 0.0,
    seed: int = 0,
) -> List[float]:
    """Simulate: e_{k+1} = c * e_k (+ optional noise)."""
    import random
    random.seed(seed)
    e = e0
    out = [e0]
    for _ in range(steps - 1):
        e = c * e
        if noise:
            e += random.uniform(-noise, noise)
        out.append(e)
    return out

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
