"""Tiny numeric helpers (standard library only)."""
from __future__ import annotations

import math
from typing import Iterable, Sequence


def clamp(x: float, lo: float, hi: float) -> float:
    return lo if x < lo else hi if x > hi else x


def finite(x) -> bool:
    try:
        return x is not None and math.isfinite(float(x))
    except (TypeError, ValueError):
        return False


def pnnl_ema(values: Sequence[float]) -> float:
    """The exact EMA used by PNNL's deployed optimal-start agent.

    smoothing = min(1, 4 / (n + 1)); newest value weighted most. With n <= 3
    this is simply the newest value. Ported from aems-edge manager/utils.py.
    """
    n = len(values)
    if n == 0:
        raise ValueError("empty")
    s = min(1.0, 2.0 / (n + 1.0) * 2.0)
    rev = list(values)[::-1]
    out = 0.0
    for i in range(n):
        out += rev[i] * s * (1.0 - s) ** i
    out += rev[-1] * (1.0 - s) ** n
    return out


def ema_update(old: float, new: float, w: float) -> float:
    """alpha_k = alpha_{k-1} + w (new - alpha_{k-1})  (paper Eq. 24)."""
    return old + w * (new - old)


def median(values: Iterable[float]) -> float:
    v = sorted(values)
    n = len(v)
    if n == 0:
        raise ValueError("empty")
    m = n // 2
    return v[m] if n % 2 else 0.5 * (v[m - 1] + v[m])


def quantile(values: Sequence[float], q: float) -> float:
    """Linear-interpolated quantile, q in [0, 1]."""
    v = sorted(values)
    if not v:
        raise ValueError("empty")
    if len(v) == 1:
        return v[0]
    pos = clamp(q, 0.0, 1.0) * (len(v) - 1)
    lo = int(math.floor(pos))
    hi = min(lo + 1, len(v) - 1)
    return v[lo] + (v[hi] - v[lo]) * (pos - lo)


def mad_scale(values: Sequence[float]) -> float:
    """Robust standard deviation estimate: 1.4826 * median absolute deviation."""
    if not values:
        return 0.0
    m = median(values)
    return 1.4826 * median(abs(x - m) for x in values)


class RLS:
    """Recursive least squares with exponential forgetting (pure Python).

    theta  <- theta + K (y - x.theta),  K = P x / (lam + x' P x)
    P      <- (P - K x' P) / lam
    """

    def __init__(self, theta0: Sequence[float], p0: Sequence[float], lam: float = 0.97):
        self.theta = [float(t) for t in theta0]
        n = len(self.theta)
        self.P = [[(float(p0[i]) if i == j else 0.0) for j in range(n)] for i in range(n)]
        self.lam = float(lam)
        self.n_updates = 0

    def predict(self, x: Sequence[float]) -> float:
        return sum(t * xi for t, xi in zip(self.theta, x))

    def update(self, x: Sequence[float], y: float) -> None:
        n = len(self.theta)
        Px = [sum(self.P[i][j] * x[j] for j in range(n)) for i in range(n)]
        denom = self.lam + sum(x[i] * Px[i] for i in range(n))
        if denom <= 1e-12:
            return
        K = [p / denom for p in Px]
        err = y - self.predict(x)
        self.theta = [self.theta[i] + K[i] * err for i in range(n)]
        xP = [sum(x[i] * self.P[i][j] for i in range(n)) for j in range(n)]
        self.P = [[(self.P[i][j] - K[i] * xP[j]) / self.lam for j in range(n)] for i in range(n)]
        # keep P symmetric and bounded (numerical hygiene for long runs)
        for i in range(n):
            for j in range(i + 1, n):
                s = 0.5 * (self.P[i][j] + self.P[j][i])
                self.P[i][j] = self.P[j][i] = s
            self.P[i][i] = clamp(self.P[i][i], 1e-9, 1e9)
        self.n_updates += 1
