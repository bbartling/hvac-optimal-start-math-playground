"""Optimal-start response-time models.

Every model answers one question for ONE zone (or one critical-zone group):
"starting now, how many minutes until the zone reaches its occupied
setpoint?"  ``predict`` returns minutes (or ``None`` when it has no history;
the planner then falls back to the configured maximum lead, which is exactly
what PNNL's deployed agent does). ``update`` learns from one
:class:`~hvac_optimal.types.RecoveryEvent` after the morning is over.

Models
------
* ``FixedLead``            conventional fixed schedule (60-120 min) baseline
* ``LinearRateEMA``        repo Model 0 (Tridium kitControl style deg/min EMA)
* ``PNNLModel1Quadratic``  paper Model 1, Eqs. 12-14 (vendor "Johnson")
* ``PNNLModel2OatRatio``   paper Model 2, Eqs. 15-16 (vendor "Carrier")
* ``PNNLModel3Regression`` paper Model 3, Eqs. 17-20 (vendor "Siemens")
* ``PNNLModel4Exponential``paper Model 4, Eqs. 21-23 (Smart Building Start)
* ``PNNLMedianEnsemble``   median of Models 1-4, as PNNL's deployed agent does
* ``RepoSGDModel5``        repo Model 5 (gradient-descent with Monday flag)
* ``RobustRLSStart``       new: robust recursive regression + post-weekend
                           term + self-calibrating residual-quantile margin

Faithfulness notes are in each class docstring. All temperatures in one
consistent unit; PNNL constants assume deg F.
"""
from __future__ import annotations

import math
from typing import Callable, Dict, List, Optional

from ._stats import RLS, clamp, finite, mad_scale, median, pnnl_ema, quantile
from .types import Mode, RecoveryEvent


def _deficit(mode: Mode, temp: float, target: float) -> float:
    return max(0.0, target - temp) if mode == "heat" else max(0.0, temp - target)


def _trim(lst: list, value: float, window: int) -> list:
    if finite(value):
        lst.append(float(value))
    return lst[-window:]


class StartModel:
    """Base class. Subclasses implement ``_predict`` and ``_update``."""

    name = "base"
    #: True if the model wants the post_weekend flag in predict/update
    uses_post_weekend = False

    def predict(self, mode: Mode, temp: float, target: float, oat: float,
                post_weekend: bool = False) -> Optional[float]:
        if mode not in ("heat", "cool"):
            return 0.0
        if _deficit(mode, temp, target) <= 0:
            return 0.0
        out = self._predict(mode, temp, target, oat, post_weekend)
        if out is None or not finite(out):
            return None
        return max(0.0, float(out))

    def update(self, event: RecoveryEvent) -> None:
        if event.mode not in ("heat", "cool") or event.delta <= 0:
            return
        self._update(event)

    # -- to implement --
    def _predict(self, mode, temp, target, oat, post_weekend):  # pragma: no cover
        raise NotImplementedError

    def _update(self, event):  # pragma: no cover
        raise NotImplementedError


# ---------------------------------------------------------------------------
class FixedLead(StartModel):
    """Conventional schedule: always start ``minutes`` before occupancy."""

    def __init__(self, minutes: float = 120.0):
        self.minutes = float(minutes)
        self.name = f"fixed_{int(minutes)}"

    def predict(self, mode, temp, target, oat, post_weekend=False):
        return self.minutes

    def _update(self, event):
        pass


# ---------------------------------------------------------------------------
class LinearRateEMA(StartModel):
    """Repo Model 0: t = dT / R, R (deg/min) tracked with an EMA.

    ``R_new = R_old + w (dT/t_act - R_old)``; R kept above ``min_rate``.
    ``buffer_min`` and ``safety`` reproduce the vavrl / v6 style margins.
    With ``w = 0`` the rate never learns (the vavrl static supervisor).
    """

    name = "m0_linear_ema"

    def __init__(self, heat_rate: float = 0.1, cool_rate: float = 0.1, w: float = 0.2,
                 safety: float = 1.0, buffer_min: float = 0.0, min_rate: float = 0.005):
        self.rate = {"heat": float(heat_rate), "cool": float(cool_rate)}
        self.w = float(w)
        self.safety = float(safety)
        self.buffer = float(buffer_min)
        self.min_rate = float(min_rate)

    def _predict(self, mode, temp, target, oat, post_weekend):
        return _deficit(mode, temp, target) / max(self.min_rate, self.rate[mode]) * self.safety + self.buffer

    def _update(self, e):
        if not e.minutes_to_target or e.minutes_to_target <= 0 or self.w <= 0:
            return
        today = e.delta / e.minutes_to_target
        self.rate[e.mode] = max(self.min_rate, self.rate[e.mode] + self.w * (today - self.rate[e.mode]))


# ---------------------------------------------------------------------------
class _PNNLBase(StartModel):
    """Shared PNNL conventions: rolling window of daily parameters + PNNL EMA."""

    def __init__(self, window: int = 8):
        self.window = int(window)


class PNNLModel1Quadratic(_PNNLBase):
    """Paper Model 1 (Eqs. 12-14), as deployed by PNNL ("Johnson" class).

    t = a (Tsp - Tz0)^2 + b
    b = minutes per degree over the first degree of recovery (Eq. 14)
    a = (t_act - b) / dT0^2 (Eq. 13); if t_act - b < 1 then a = t_act / (10 dT)
    Daily a, b kept in a rolling window (8 days) and combined with PNNL's EMA.
    """

    name = "pnnl_m1_quadratic"

    def __init__(self, window: int = 8):
        super().__init__(window)
        self.a: Dict[str, list] = {"heat": [], "cool": []}
        self.b: Dict[str, list] = {"heat": [], "cool": []}

    def _predict(self, mode, temp, target, oat, post_weekend):
        if not self.a[mode] or not self.b[mode]:
            return None
        d = _deficit(mode, temp, target)
        return pnnl_ema(self.a[mode]) * d * d + pnnl_ema(self.b[mode])

    def _update(self, e):
        t = e.minutes_to_target
        b = e.minutes_for_first_degree(1.0)
        if not t or t <= 0 or b is None:
            return
        if t - b >= 1:
            a = (t - b) / (e.delta ** 2)
        else:
            a = t / (e.delta * 10.0)
        if a < 0 or b < 0:
            return
        self.a[e.mode] = _trim(self.a[e.mode], a, self.window)
        self.b[e.mode] = _trim(self.b[e.mode], b, self.window)


class PNNLModel2OatRatio(_PNNLBase):
    """Paper Model 2 (Eqs. 15-16), as deployed by PNNL ("Carrier" class).

    t = dT / alpha * (To_ref - To_prev) / (To_ref - To_now)
    alpha = degrees recovered / minutes (Eq. 16), To_ref = 0 F heating,
    100 F cooling (ASHRAE). ``To_prev`` = EMA of training-day OAT.
    Guard (not in the paper): the OAT ratio is undefined when OAT crosses the
    reference (e.g. Fairbanks below 0 F); it is then set to 1 and otherwise
    clipped to [0.25, 4] so one sensor glitch cannot command a 0 or 1000 min start.
    """

    name = "pnnl_m2_oat_ratio"

    def __init__(self, window: int = 8, oat_ref_heat: float = 0.0, oat_ref_cool: float = 100.0):
        super().__init__(window)
        self.rate: Dict[str, list] = {"heat": [], "cool": []}
        self.oat: Dict[str, list] = {"heat": [], "cool": []}
        self.ref = {"heat": float(oat_ref_heat), "cool": float(oat_ref_cool)}

    def _predict(self, mode, temp, target, oat, post_weekend):
        if not self.rate[mode]:
            return None
        r = pnnl_ema(self.rate[mode])
        if r <= 0:
            return None
        ref = self.ref[mode]
        prev = pnnl_ema(self.oat[mode]) if self.oat[mode] else oat
        num, den = ref - oat, ref - prev
        ratio = num / den if abs(den) > 1e-6 else 1.0
        if not finite(ratio) or ratio <= 0:
            ratio = 1.0
        ratio = clamp(ratio, 0.25, 4.0)
        return _deficit(mode, temp, target) / (ratio * r)

    def _update(self, e):
        t = e.minutes_to_target
        if not t or t <= 0:
            return
        rate = e.delta / t
        if rate <= 0:
            return
        self.rate[e.mode] = _trim(self.rate[e.mode], rate, self.window)
        self.oat[e.mode] = _trim(self.oat[e.mode], e.oat_mean if e.oat_mean is not None else e.oat, self.window)


class PNNLModel3Regression(_PNNLBase):
    """Paper Model 3 (Eqs. 17-20).

    t = a dT + b dT (Tsp - To) / c + d
    a  = minutes per degree over the first degree (Eq. 18)
    b  = (t_act - a dT0) c / (dT0 (Tsp - To))  (Eq. 19, clipped >= 0 as PNNL does)
    c  = 10 (PNNL's scale constant; the paper's alpha_3c)
    d  = day-to-day correction (Eq. 20): +e if the zone was > 1 deg short of
         setpoint at occupancy yesterday, -e if it overshot by > 1 deg; reset to
         0 when |d| exceeds ``d_reset``.
    """

    name = "pnnl_m3_regression"

    def __init__(self, window: int = 8, c: float = 10.0, step_e: float = 5.0,
                 d_reset: float = 60.0, band: float = 1.0):
        super().__init__(window)
        self.a: Dict[str, list] = {"heat": [], "cool": []}
        self.b: Dict[str, list] = {"heat": [], "cool": []}
        self.d = {"heat": 0.0, "cool": 0.0}
        self.c, self.step_e, self.d_reset, self.band = float(c), float(step_e), float(d_reset), float(band)

    @staticmethod
    def _load(mode, target, oat):
        return (target - oat) if mode == "heat" else (oat - target)

    def _predict(self, mode, temp, target, oat, post_weekend):
        if not self.a[mode]:
            return None
        d = _deficit(mode, temp, target)
        load = max(0.0, self._load(mode, target, oat))
        b = pnnl_ema(self.b[mode]) if self.b[mode] else 0.0
        return pnnl_ema(self.a[mode]) * d + b * d * load / self.c + self.d[mode]

    def _update(self, e):
        t = e.minutes_to_target
        a = e.minutes_for_first_degree(1.0)
        if not t or t <= 0:
            return
        if a is None:
            a = t / e.delta
        load = self._load(e.mode, e.target, e.oat)
        if load > 0.5:
            b = (t - a * e.delta) * self.c / (e.delta * load)
            b = max(0.0, b)
        else:
            b = 0.0
        self.a[e.mode] = _trim(self.a[e.mode], a, self.window)
        self.b[e.mode] = _trim(self.b[e.mode], b, self.window)
        if e.arrival_error is not None:
            dd = self.d[e.mode]
            if e.arrival_error > self.band:
                dd += self.step_e
            elif e.arrival_error < -self.band:
                dd -= self.step_e
            if abs(dd) > self.d_reset:
                dd = 0.0
            self.d[e.mode] = dd


class PNNLModel4Exponential(_PNNLBase):
    """Paper Model 4 (Eqs. 21-23), Smart Building Start ("Sbs" class).

    t = ln(a / b) / ln(c)
    a = allowable deviation from setpoint (``deviation``; PNNL default 1 F)
    b = current deviation of the zone from the comfort band
    c = per-minute decay factor of the error, least squares over the recovery:
        c = sum(e_{i-1} e_i) / sum(e_{i-1}^2)  (Eq. 23), clipped to [0.001, 0.999]
    The trajectory may be sampled at any fixed interval; c is converted to a
    per-minute factor. Initial c = exp(-1 / (earliest + latest start)).
    """

    name = "pnnl_m4_exponential"

    def __init__(self, window: int = 8, deviation: float = 1.0, earliest: float = 180.0,
                 latest: float = 10.0):
        super().__init__(window)
        self.deviation = float(deviation)
        self.c_list: Dict[str, list] = {"heat": [], "cool": []}
        self.c_default = math.exp(-1.0 / (earliest + latest))

    def _c(self, mode):
        return pnnl_ema(self.c_list[mode]) if self.c_list[mode] else self.c_default

    def _predict(self, mode, temp, target, oat, post_weekend):
        err = _deficit(mode, temp, target)
        if err <= self.deviation:
            return 0.0
        c = clamp(self._c(mode), 0.001, 0.999)
        return math.log(self.deviation / err) / math.log(c)

    def _update(self, e):
        traj = list(e.trajectory)
        if len(traj) < 3:
            return
        steps = [traj[i + 1][0] - traj[i][0] for i in range(len(traj) - 1)]
        dt = median(steps)
        if dt <= 0:
            return
        errs = [_deficit(e.mode, temp, e.target) for _, temp in traj]
        sxy = sum(errs[i - 1] * errs[i] for i in range(1, len(errs)))
        sxx = sum(errs[i - 1] ** 2 for i in range(1, len(errs)))
        if sxx <= 0 or sxy <= 0:
            return
        c_step = clamp(sxy / sxx, 0.001, 0.999)
        c_min = c_step ** (1.0 / dt)
        self.c_list[e.mode] = _trim(self.c_list[e.mode], clamp(c_min, 0.001, 0.999), self.window)


class PNNLMedianEnsemble(StartModel):
    """PNNL's deployed aggregation: median of Models 1-4.

    Models without history count as ``earliest`` (the PNNL default), and the
    median is clipped to [latest, earliest] by the planner. With
    ``post_weekend_split=True`` a second set of models (window 4) is trained
    only on days after weekends/holidays and used on those days once trained,
    exactly like ``OptimalStartManager`` in PNNL's aems-edge code.
    """

    uses_post_weekend = True

    def __init__(self, post_weekend_split: bool = False, earliest: float = 180.0,
                 window: int = 8, deviation: float = 1.0):
        self.earliest = float(earliest)
        self.split = bool(post_weekend_split)
        self.name = "pnnl_deployed_median_split" if self.split else "pnnl_median"
        self.sets = {False: self._make(window, deviation)}
        if self.split:
            self.sets[True] = self._make(4, deviation)
        self.trained_we = False

    @staticmethod
    def _make(window, deviation):
        return [PNNLModel1Quadratic(window), PNNLModel2OatRatio(window),
                PNNLModel3Regression(window), PNNLModel4Exponential(window, deviation)]

    def _predict(self, mode, temp, target, oat, post_weekend):
        use_we = self.split and post_weekend and self.trained_we
        vals = []
        for m in self.sets[use_we]:
            p = m.predict(mode, temp, target, oat, post_weekend)
            vals.append(self.earliest if p is None else p)
        return median(vals)

    def _update(self, e):
        key = bool(self.split and e.post_weekend)
        if key:
            self.trained_we = True
        for m in self.sets[key]:
            m.update(e)


# ---------------------------------------------------------------------------
class RepoSGDModel5(StartModel):
    """Repo Model 5: t = w1 * (dT / dT_max) + w2 * IsMonday + bias.

    Trained exactly like ``model_five_tutorial.py``: batch gradient descent
    (lr 0.01, 2000 epochs, weights start at 0.5, bias 0) over the recovery
    history (last ``window`` events), refit after every event.
    """

    name = "repo_m5_sgd"
    uses_post_weekend = True

    def __init__(self, dt_max: float = 20.0, lr: float = 0.01, epochs: int = 2000, window: int = 30):
        self.dt_max, self.lr, self.epochs, self.window = float(dt_max), float(lr), int(epochs), int(window)
        self.hist: Dict[str, list] = {"heat": [], "cool": []}
        self.w: Dict[str, Optional[list]] = {"heat": None, "cool": None}

    def _predict(self, mode, temp, target, oat, post_weekend):
        w = self.w[mode]
        if w is None:
            return None
        x = (_deficit(mode, temp, target) / self.dt_max, 1.0 if post_weekend else 0.0)
        return w[0] * x[0] + w[1] * x[1] + w[2]

    def _update(self, e):
        if not e.minutes_to_target:
            return
        h = self.hist[e.mode]
        h.append((e.delta / self.dt_max, 1.0 if e.post_weekend else 0.0, float(e.minutes_to_target)))
        del h[:-self.window]
        w1, w2, b = 0.5, 0.5, 0.0
        n = len(h)
        for _ in range(self.epochs):
            g1 = g2 = gb = 0.0
            for x1, x2, y in h:
                err = w1 * x1 + w2 * x2 + b - y
                g1 += err * x1
                g2 += err * x2
                gb += err
            w1 -= self.lr * 2.0 / n * g1
            w2 -= self.lr * 2.0 / n * g2
            b -= self.lr * 2.0 / n * gb
        self.w[e.mode] = [w1, w2, b]


# ---------------------------------------------------------------------------
class RobustRLSStart(StartModel):
    """New model: robust, self-calibrating regression (the benchmark candidate).

    Point model (minutes), per mode::

        t = th0 * dT + th1 * dT * load / 10 + th2 * PW * dT + th3

    where ``load`` = setpoint - OAT (heating) or OAT - setpoint (cooling),
    clipped at 0, and ``PW`` = 1 on the first occupied day after a weekend or
    holiday (the paper's documented Monday failure). Parameters are learned by
    recursive least squares with forgetting (``lam``) from a physical prior
    (``prior_min_per_deg`` minutes per degree) so day 1 is sane. Outliers are
    Huber-clipped at ``huber_k`` robust standard deviations before updating.

    Safety margin: the out-of-sample residuals (actual - predicted, computed
    BEFORE each update) are kept in a rolling window; the prediction adds their
    ``q`` quantile (separately for post-weekend days once there are enough).
    A model that is biased late learns a positive margin, one that starts too
    early learns a negative margin, so arrival converges to the target
    lateness probability 1 - q without hand tuning.
    """

    name = "robust_rls"
    uses_post_weekend = True

    def __init__(self, prior_min_per_deg: float = 15.0, lam: float = 0.97, q: float = 0.8,
                 window: int = 15, pw_window: int = 6, huber_k: float = 2.5,
                 use_post_weekend: bool = True, use_load: bool = True):
        self.prior = float(prior_min_per_deg)
        self.lam, self.q = float(lam), float(q)
        self.window, self.pw_window = int(window), int(pw_window)
        self.huber_k = float(huber_k)
        self.use_pw, self.use_load = bool(use_post_weekend), bool(use_load)
        self.rls = {m: RLS([self.prior, 0.0, 0.0, 0.0], [400.0, 400.0, 400.0, 900.0], lam) for m in ("heat", "cool")}
        self.res = {(m, pw): [] for m in ("heat", "cool") for pw in (False, True)}
        self.n = {"heat": 0, "cool": 0}

    def _x(self, mode, d, target, oat, pw):
        load = max(0.0, (target - oat) if mode == "heat" else (oat - target)) if self.use_load else 0.0
        return [d, d * load / 10.0, d * (1.0 if (pw and self.use_pw) else 0.0), 1.0]

    def point(self, mode, temp, target, oat, post_weekend=False) -> float:
        d = _deficit(mode, temp, target)
        return max(0.0, self.rls[mode].predict(self._x(mode, d, target, oat, post_weekend)))

    def margin(self, mode, post_weekend=False) -> float:
        pw = bool(post_weekend and self.use_pw)
        r = self.res[(mode, pw)]
        if pw and len(r) < 2:
            r = self.res[(mode, False)]
        if len(r) < 3:
            return 0.0
        return quantile(r, self.q)

    def _predict(self, mode, temp, target, oat, post_weekend):
        return self.point(mode, temp, target, oat, post_weekend) + self.margin(mode, post_weekend)

    def _update(self, e):
        t = e.minutes_to_target
        if t is None or t <= 0:
            return
        pw = bool(e.post_weekend and self.use_pw)
        x = self._x(e.mode, e.delta, e.target, e.oat, e.post_weekend)
        pred = max(0.0, self.rls[e.mode].predict(x))
        resid = t - pred
        hist = self.res[(e.mode, pw)]
        hist.append(resid)
        del hist[:-(self.pw_window if pw else self.window)]
        scale = max(5.0, mad_scale(self.res[(e.mode, False)] or [resid]))
        y = pred + clamp(resid, -self.huber_k * scale, self.huber_k * scale) if self.n[e.mode] >= 3 else t
        self.rls[e.mode].update(x, y)
        self.n[e.mode] += 1


# ---------------------------------------------------------------------------
START_MODELS: Dict[str, Callable[[], StartModel]] = {
    "fixed_60": lambda: FixedLead(60),
    "fixed_90": lambda: FixedLead(90),
    "fixed_120": lambda: FixedLead(120),
    "fixed_180": lambda: FixedLead(180),
    # vavrl static supervisor: 1.5 F/h heat, 1.2 F/h cool, +15 min, never learns
    "vavrl_static": lambda: _named(LinearRateEMA(1.5 / 60, 1.2 / 60, w=0.0, buffer_min=15.0), "vavrl_static"),
    "m0_linear_ema": lambda: LinearRateEMA(),
    "pnnl_m1_quadratic": lambda: PNNLModel1Quadratic(),
    "pnnl_m2_oat_ratio": lambda: PNNLModel2OatRatio(),
    "pnnl_m3_regression": lambda: PNNLModel3Regression(),
    "pnnl_m4_exponential": lambda: PNNLModel4Exponential(),
    "pnnl_median": lambda: PNNLMedianEnsemble(False),
    "pnnl_deployed_median_split": lambda: PNNLMedianEnsemble(True),
    "repo_m5_sgd": lambda: RepoSGDModel5(),
    "robust_rls": lambda: RobustRLSStart(),
    "robust_rls_no_pw": lambda: _named(RobustRLSStart(use_post_weekend=False), "robust_rls_no_pw"),
}


def _named(model: StartModel, name: str) -> StartModel:
    model.name = name
    return model


def make_start_model(name: str) -> StartModel:
    try:
        return START_MODELS[name]()
    except KeyError:
        raise KeyError(f"unknown start model {name!r}; choose from {sorted(START_MODELS)}") from None
