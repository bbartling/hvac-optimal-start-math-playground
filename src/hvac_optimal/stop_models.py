"""Optimal-stop (early shut-off / coast-down) drift models.

A stop model answers: "if the air handler is switched off now, where can this
zone's temperature be after ``minutes``?" as a (low, high) bound. The stop
planner switches off only if every zone's bound stays inside the occupied
band (minus a guard) until the end of occupancy.

Models
------
* ``NoEarlyStop``      baseline, never stops early
* ``ConstantDrift``    fixed drift rate both ways (vavrl supervisor: 0.35 F/h)
* ``RecoveryRateProxy``drift = learned HVAC *recovery* rate x safety, both ways
                       (the neurips v6/v7 G36 backbone's proxy). Physically it
                       is a recovery rate, not a coasting rate.
* ``LinearDriftEMA``   learned signed drift rate (deg/h) while off, EMA
* ``FirstOrderCoast``  learned first-order (1R1C) coast model, the same
                       thermal-decay physics behind PNNL Model 4 / Eq. 3 with
                       Q_RTU = 0:  dT/dt = a (OAT - T) + b + b_occ * occupied
                       fitted by recursive least squares on OFF intervals.
"""
from __future__ import annotations

import math
from typing import Callable, Dict, Optional, Tuple

from ._stats import RLS, clamp, mad_scale
from .types import CoastSample

Bounds = Tuple[float, float]


class StopModel:
    name = "base"
    never_stops = False

    def bounds(self, temp: float, oat: float, minutes: float, occupied: bool = True) -> Optional[Bounds]:
        raise NotImplementedError

    def update(self, s: CoastSample) -> None:
        pass


class NoEarlyStop(StopModel):
    name = "no_early_stop"
    never_stops = True

    def bounds(self, temp, oat, minutes, occupied=True):
        return None


class ConstantDrift(StopModel):
    """T can move ``rate`` deg/h in either direction (vavrl default 0.35 F/h)."""

    name = "vavrl_const_drift"

    def __init__(self, rate_per_h: float = 0.35):
        self.rate = float(rate_per_h)

    def bounds(self, temp, oat, minutes, occupied=True):
        d = self.rate * minutes / 60.0
        return temp - d, temp + d


class RecoveryRateProxy(StopModel):
    """v6/v7 backbone proxy: drift = max(floor, recovery_rate * safety)."""

    name = "recovery_rate_proxy"

    def __init__(self, rate_fn: Callable[[], Tuple[float, float]], safety: float = 1.25, floor: float = 0.54):
        self.rate_fn, self.safety, self.floor = rate_fn, float(safety), float(floor)

    def bounds(self, temp, oat, minutes, occupied=True):
        heat_rate, cool_rate = self.rate_fn()
        h = minutes / 60.0
        return (temp - max(self.floor, heat_rate * self.safety) * h,
                temp + max(self.floor, cool_rate * self.safety) * h)


class LinearDriftEMA(StopModel):
    """Signed drift rate (deg/h) learned with an EMA, +/- k robust sigma."""

    name = "linear_drift_ema"

    def __init__(self, w: float = 0.05, k: float = 2.0, prior_rate: float = 0.0, prior_spread: float = 1.0):
        self.w, self.k = float(w), float(k)
        self.rate = {False: float(prior_rate), True: float(prior_rate)}
        self.hist = {False: [], True: []}
        self.prior_spread = float(prior_spread)

    def bounds(self, temp, oat, minutes, occupied=True):
        occ = bool(occupied) if self.hist[True] else False
        h = minutes / 60.0
        r = self.rate[occ]
        hist = self.hist[occ]
        spread = mad_scale(hist) if len(hist) >= 12 else self.prior_spread
        # spread of 5-min rates shrinks when averaged over the horizon
        n = max(1.0, minutes / 5.0)
        unc = self.k * spread / math.sqrt(n) * h
        mid = temp + r * h
        return mid - unc, mid + unc

    def update(self, s: CoastSample):
        if s.minutes <= 0:
            return
        r = (s.temp_end - s.temp_start) / (s.minutes / 60.0)
        occ = bool(s.occupied)
        self.rate[occ] = self.rate[occ] + self.w * (r - self.rate[occ])
        self.hist[occ].append(r)
        del self.hist[occ][:-288]


class FirstOrderCoast(StopModel):
    """1R1C coast: dT/dt [deg/h] = a (OAT - T) + b + c * occupied.

    Learned by RLS with forgetting on OFF intervals. Projection uses the exact
    exponential solution with OAT held at its current value. Bounds widen by
    ``k`` robust sigma of the rate residuals, averaged over the horizon, plus a
    small structural term ``struct`` deg/h for model error.
    """

    name = "first_order_coast"

    def __init__(self, lam: float = 0.999, k: float = 2.0, struct: float = 0.15,
                 min_samples: int = 24, unseen_occ: str = "gain"):
        if unseen_occ not in ("gain", "union"):
            raise ValueError("unseen_occ must be 'gain' or 'union'")
        self.unseen_occ = unseen_occ
        self.rls = RLS([0.05, 0.0, 0.3], [0.01, 1.0, 1.0], lam)
        self.k, self.struct, self.min_samples = float(k), float(struct), int(min_samples)
        self.resid: list = []
        self.n = 0
        self.n_occ = 0

    def bounds(self, temp, oat, minutes, occupied=True):
        if self.n < self.min_samples:
            return None  # not trained: planner will not stop early
        a, b, c = self.rls.theta
        h = minutes / 60.0
        sigma = mad_scale(self.resid) if len(self.resid) >= 12 else 1.0
        unc = (self.k * sigma / math.sqrt(max(1.0, minutes / 5.0)) + self.struct) * h
        seen = self.n_occ >= 6
        if not occupied or seen:
            mid = self._project(temp, oat, h, a, b + (c if occupied else 0.0))
            return mid - unc, mid + unc
        if self.unseen_occ == "gain":
            # benchmarked default: assume at least +0.5 deg/h internal gains
            mid = self._project(temp, oat, h, a, b + max(c, 0.5))
            return mid - unc, mid + unc
        # "union": occupied gains unknown, so cover both no gains and +1 deg/h gains
        lo = self._project(temp, oat, h, a, b)
        hi = self._project(temp, oat, h, a, b + 1.0)
        return min(lo, hi) - unc, max(lo, hi) + unc

    @staticmethod
    def _project(temp: float, oat: float, h: float, a: float, drive: float) -> float:
        a = max(a, 1e-4)
        t_inf = oat + drive / a
        return t_inf + (temp - t_inf) * math.exp(-a * h)

    def update(self, s: CoastSample):
        if s.minutes <= 0:
            return
        h = s.minutes / 60.0
        y = (s.temp_end - s.temp_start) / h
        x = [s.oat - s.temp_start, 1.0, 1.0 if s.occupied else 0.0]
        pred = self.rls.predict(x)
        self.resid.append(y - pred)
        del self.resid[:-288]
        self.rls.update(x, y)
        self.n += 1
        if s.occupied:
            self.n_occ += 1


STOP_MODELS: Dict[str, Callable[[], StopModel]] = {
    "no_early_stop": NoEarlyStop,
    "vavrl_const_drift": ConstantDrift,
    "linear_drift_ema": LinearDriftEMA,
    "first_order_coast": FirstOrderCoast,
    "first_order_coast_union": lambda: FirstOrderCoast(unseen_occ="union"),
}


def make_stop_model(name: str) -> StopModel:
    try:
        return STOP_MODELS[name]()
    except KeyError:
        raise KeyError(f"unknown stop model {name!r}; choose from {sorted(STOP_MODELS)}") from None
