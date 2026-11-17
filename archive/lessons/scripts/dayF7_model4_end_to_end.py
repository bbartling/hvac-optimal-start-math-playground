from __future__ import annotations
from typing import List
from scripts.helpers import (
    simulate_first_order_errors,
    estimate_c_least_squares,
    model4_topt_minutes,
    ema,
    clamp,
)

def build_errors_from_temps(Tsp: float, Tzs: List[float], mode: str) -> List[float]:
    """Choose ONE sign convention so errors decay toward zero."""
    errors: List[float] = []
    for Tz in Tzs:
        if mode == "heating":
            errors.append(Tsp - Tz)
        else:
            errors.append(Tz - Tsp)
    return errors

def main() -> None:
    print("--- Day F7: Model 4 mini end-to-end ---")

    # configuration knobs
    mode = "cooling"          # or "heating"
    Tsp = 74.0                # occupied setpoint
    deadband = 0.5            # acceptable remaining error (°F)
    sample_minutes = 1        # sample period (minutes)
    N = 12                    # batch length after startup
    c_min, c_max = 0.80, 0.99
    max_minutes = 180.0       # hard cap (guardrail)
    ema_w = 0.30              # smoothing weight

    # pretend we just started the unit and collected a window of temps
    true_c = 0.90
    e0 = 6.0
    errors_true = simulate_first_order_errors(e0=e0, c=true_c, steps=N, noise=0.05, seed=1)

    # Convert simulated errors to temps (demo only)
    if mode == "cooling":
        # error = Tz - Tsp  => Tz = Tsp + error
        Tzs = [Tsp + e for e in errors_true]
    else:
        # error = Tsp - Tz  => Tz = Tsp - error
        Tzs = [Tsp - e for e in errors_true]

    errors = build_errors_from_temps(Tsp, Tzs, mode)
    print("first 6 errors:", [round(e, 3) for e in errors[:6]])

    # estimate c from the batch
    c_new = estimate_c_least_squares(errors)
    c_new = clamp(c_new, c_min, c_max)
    print("estimated c (clamped):", round(c_new, 4))

    # EMA smooth c across days (pretend prior c_ema exists)
    c_ema = 0.92
    c_ema = ema(c_ema, c_new, ema_w)
    print("c_ema:", round(c_ema, 4))

    # compute t_opt
    t_opt = model4_topt_minutes(deadband_deg=deadband, e0=errors[0], c=c_ema) * sample_minutes
    t_opt = min(t_opt, max_minutes)
    print("t_opt (guardrailed):", round(t_opt, 2), "minutes")

if __name__ == "__main__":
    main()
