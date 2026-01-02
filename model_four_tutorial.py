"""
Model 4 (PNNL-style) — Complete Demo Script

What this script shows:
1) A human-readable "history" list (ΔT, minutes) like BAS folks expect.
2) A synthetic dataset generated from Model 4 physics:
      t = τ * ln(1 + k * ΔT)     <-- LOG MATH (Model 4 equation)
3) An ITERATIVE fit of τ and k using gradient descent (nonlinear regression).
4) A printed table so people can SEE the data structure.

No external libs required (just math, random).
"""

import math
import random
from typing import List, Dict, Tuple


# ------------------------------------------------------------
# 1) Human-readable history (operator style)
# ------------------------------------------------------------
history: List[List[float]] = [
    [2.0, 10.0],   # Day 1:  ΔT=2°F took 10 min
    [5.0, 25.0],   # Day 2
    [8.0, 40.0],   # Day 3
    [3.0, 15.0],   # Day 4
    [6.0, 29.0],   # Day 5
    [10.0, 50.0],  # Day 6
    [4.0, 19.0],   # Day 7
    [5.5, 27.0],   # Day 8
    [9.0, 45.0],   # Day 9
    [2.5, 12.0],   # Day 10
    [7.0, 36.0],   # Day 11
    [6.5, 32.0],   # Day 12
    [3.5, 17.0],   # Day 13
    [8.5, 42.0],   # Day 14
    [4.5, 22.0],   # Day 15
]


def print_history_table(hist: List[List[float]], title: str) -> None:
    print("\n" + title)
    print("-" * len(title))
    print(f"{'Day':>4}  {'ΔT (deg)':>8}  {'Actual mins':>11}  {'Rate (deg/min)':>14}")
    for i, (dT, mins) in enumerate(hist, start=1):
        rate = dT / mins if mins > 0 else float("nan")
        print(f"{i:>4}  {dT:>8.2f}  {mins:>11.2f}  {rate:>14.4f}")


# ------------------------------------------------------------
# 2) Model 4 prediction equation (closed-form)
# ------------------------------------------------------------
def model4_predict_minutes(deltaT: float, tau: float, k: float) -> float:
    """
    Model 4 LOG MATH is here:

        t_pred = τ * ln(1 + k * ΔT)

    This part is NOT iterative. It's a direct formula.
    """
    z = 1.0 + k * deltaT
    z = max(z, 1e-9)  # safety: keep log domain valid
    return tau * math.log(z)


# ------------------------------------------------------------
# 3) Synthetic data generator using Model 4 physics
# ------------------------------------------------------------
def generate_fake_model4_data(
    n: int = 30,
    tau_true: float = 25.0,
    k_true: float = 0.18,
    noise_std: float = 1.5,
    seed: int = 7,
) -> List[Dict[str, float]]:
    """
    Generates a list of dict rows so people can "see" the data structure:

      {"day": 1, "deltaT": 7.3, "actual_minutes": 32.8}

    Model 4 LOG MATH is here too (used to generate the fake ground truth):
        t = τ_true * ln(1 + k_true * ΔT)
    """
    random.seed(seed)
    data: List[Dict[str, float]] = []
    for day in range(1, n + 1):
        dT = random.uniform(1.0, 12.0)

        # ==============================
        # 👉 MODEL 4 LOG MATH IS HERE 👈
        # ==============================
        t = tau_true * math.log(1.0 + k_true * dT)

        # Add random noise to simulate day-to-day uncertainty
        t += random.gauss(0.0, noise_std)

        data.append({"day": float(day), "deltaT": dT, "actual_minutes": t})
    return data


def print_data_rows(data: List[Dict[str, float]], title: str, max_rows: int = 12) -> None:
    print("\n" + title)
    print("-" * len(title))
    print(f"{'Day':>4}  {'ΔT (deg)':>8}  {'Actual mins':>11}")
    for row in data[:max_rows]:
        print(f"{int(row['day']):>4}  {row['deltaT']:>8.2f}  {row['actual_minutes']:>11.2f}")
    if len(data) > max_rows:
        print(f"... ({len(data) - max_rows} more rows)")


# ------------------------------------------------------------
# 4) Iterative fit (gradient descent) for τ and k
# ------------------------------------------------------------
def fit_model4_gradient_descent(
    data: List[Dict[str, float]],
    tau_init: float = 10.0,
    k_init: float = 0.05,
    lr_tau: float = 0.001,
    lr_k: float = 0.0005,
    steps: int = 5000,
) -> Tuple[float, float]:
    """
    This is the ITERATIVE part.

    We are solving:
        minimize sum( (t_actual - τ*ln(1+kΔT))^2 )

    τ and k are updated step-by-step (iteratively).
    """
    tau = tau_init
    k = k_init

    for step in range(steps):
        grad_tau = 0.0
        grad_k = 0.0
        sse = 0.0

        for row in data:
            dT = row["deltaT"]
            t_actual = row["actual_minutes"]

            z = 1.0 + k * dT
            z = max(z, 1e-9)

            # ==============================
            # 👉 MODEL 4 LOG MATH IS HERE 👈
            # ==============================
            t_hat = tau * math.log(z)

            err = t_hat - t_actual
            sse += err * err

            # partial derivatives:
            # d/dtau [τ ln(z)] = ln(z)
            d_hat_dtau = math.log(z)

            # d/dk [τ ln(1+kΔT)] = τ * ΔT / (1+kΔT) = τ * ΔT / z
            d_hat_dk = tau * (dT / z)

            # SSE gradient: d/dp sum(err^2) = 2*sum(err * d_hat_dp)
            grad_tau += 2.0 * err * d_hat_dtau
            grad_k += 2.0 * err * d_hat_dk

        # 🔁 ITERATIVE parameter update step
        tau -= lr_tau * grad_tau
        k -= lr_k * grad_k

        # keep k sane (so 1 + kΔT stays positive for positive ΔT)
        if k < 1e-6:
            k = 1e-6

        # occasional progress print
        if step in (0, 10, 100, 500, 1000, 2000, steps - 1):
            rmse = math.sqrt(sse / len(data))
            print(f"step={step:5d}  tau={tau:8.3f}  k={k:7.4f}  RMSE={rmse:6.3f}")

    return tau, k


def rmse_for_params(data: List[Dict[str, float]], tau: float, k: float) -> float:
    sse = 0.0
    for row in data:
        pred = model4_predict_minutes(row["deltaT"], tau, k)
        err = pred - row["actual_minutes"]
        sse += err * err
    return math.sqrt(sse / len(data))


# ------------------------------------------------------------
# 5) Main demo
# ------------------------------------------------------------
def main() -> None:
    # Show the operator-style history table
    print_history_table(history, "Operator-Style History (ΔT, minutes)")

    # Generate synthetic Model-4 data
    data = generate_fake_model4_data(n=30, tau_true=25.0, k_true=0.18, noise_std=1.5, seed=7)
    print_data_rows(data, "Synthetic Model 4 Dataset (dict rows you can see)")

    # Fit parameters iteratively
    print("\nFitting Model 4 (iterative gradient descent)...")
    tau_fit, k_fit = fit_model4_gradient_descent(
        data,
        tau_init=10.0,
        k_init=0.05,
        lr_tau=0.001,
        lr_k=0.0005,
        steps=5000,
    )

    # Final metrics
    final_rmse = rmse_for_params(data, tau_fit, k_fit)
    print("\nFinal fitted parameters")
    print("----------------------")
    print(f"tau_fit = {tau_fit:.4f}")
    print(f"k_fit   = {k_fit:.4f}")
    print(f"RMSE    = {final_rmse:.4f} min")

    # Show a few predictions vs actual
    print("\nSample predictions (actual vs predicted)")
    print("--------------------------------------")
    print(f"{'Day':>4}  {'ΔT':>6}  {'Actual':>10}  {'Pred':>10}  {'Error':>10}")
    for row in data[:10]:
        dT = row["deltaT"]
        actual = row["actual_minutes"]
        pred = model4_predict_minutes(dT, tau_fit, k_fit)
        err = pred - actual
        print(f"{int(row['day']):>4}  {dT:>6.2f}  {actual:>10.2f}  {pred:>10.2f}  {err:>10.2f}")


if __name__ == "__main__":
    main()
