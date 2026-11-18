"""
Copyright (c) 2024, Battelle Memorial Institute
All rights reserved.
Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
The views and conclusions contained in the software and documentation are those
of the authors and should not be interpreted as representing official policies,
either expressed or implied, of the FreeBSD Project.
This material was prepared as an account of work sponsored by an agency of the
United States Government. Neither the United States Government nor the United
States Department of Energy, nor Battelle, nor any of their employees, nor any
jurisdiction or organization that has cooperated in th.e development of these
materials, makes any warranty, express or implied, or assumes any legal
liability or responsibility for the accuracy, completeness, or usefulness or
any information, apparatus, product, software, or process disclosed, or
represents that its use would not infringe privately owned rights.
Reference herein to any specific commercial product, process, or service by
trade name, trademark, manufacturer, or otherwise does not necessarily
constitute or imply its endorsement, recommendation, or favoring by the
United States Government or any agency thereof, or Battelle Memorial Institute.
The views and opinions of authors expressed herein do not necessarily state or
reflect those of the United States Government or any agency thereof.
PACIFIC NORTHWEST NATIONAL LABORATORY
operated by BATTELLE for the UNITED STATES DEPARTMENT OF ENERGY
under Contract DE-AC05-76RL01830
"""
from __future__ import annotations

import math
import statistics
from dataclasses import asdict, dataclass, field
from typing import Any, Iterable, Mapping

# These are event-based research adaptations, not the frozen BAS reference.
# Temperatures and differences are in degrees Fahrenheit; elapsed time is minutes.
# See docs/model-provenance.md for source details and deliberate differences.


@dataclass(frozen=True)
class TrainingReceipt:
    """An observable fitting result; a rejected fit never silently becomes training."""

    model: str
    mode: str | None
    accepted: bool
    reason: str
    parameters: dict[str, Any] = field(default_factory=dict)
    details: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def deficit(mode: str, temp: float, target: float) -> float:
    """Distance outside the selected heating or cooling comfort boundary."""
    if mode == "heat":
        return max(0.0, target - temp)
    if mode == "cool":
        return max(0.0, temp - target)
    raise ValueError("mode must be 'heat' or 'cool'")


def pnnl_ema(values: Iterable[float]) -> float:
    """The deployed helper's finite-window EMA, initialized with the oldest value."""
    history = list(values)
    if not history:
        raise ValueError("an EMA needs at least one value")
    weight = min(1.0, 4.0 / (len(history) + 1))
    result = history[0]
    for value in history[1:]:
        result += weight * (value - result)
    return result


def _finite(value: Any) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError, OverflowError):
        return False


def _trajectory(event: Mapping[str, Any]) -> list[tuple[float, float]]:
    trace = [(float(t), float(temp)) for t, temp in event.get("traj", ())]
    if any(not _finite(t) or not _finite(temp) or t < 0 for t, temp in trace):
        raise ValueError("trajectory coordinates must be finite; elapsed time cannot be negative")
    if any(right[0] <= left[0] for left, right in zip(trace, trace[1:])):
        raise ValueError("trajectory elapsed times must strictly increase; data are not reordered")
    return trace


def minutes_per_first_degree(event: Mapping[str, Any]) -> float | None:
    """Interpolate the first actual one-degree crossing using its two adjacent samples."""
    sign = 1.0 if event["mode"] == "heat" else -1.0
    start = float(event["start"])
    previous_time, previous_gain = 0.0, 0.0
    for minute, temp in _trajectory(event):
        gain = sign * (temp - start)
        if gain >= 1.0 and gain > previous_gain:
            return previous_time + (1.0 - previous_gain) * (minute - previous_time) / (gain - previous_gain)
        previous_time, previous_gain = minute, gain
    return None


def _observed_response(event: Mapping[str, Any], allowable_deviation: float) -> tuple[float, float]:
    """Measured elapsed minutes and directional change, independent of target labels.

    A censored target time can still contain a perfectly usable rate observation.
    Event elapsed coordinates are measured from its supplied start at minute zero.
    A declared complete endpoint can supply a fallback only when no trace exists.
    """
    trace = _trajectory(event)
    mode = event["mode"]
    if trace:
        duration, end = trace[-1]
        change = end - event["start"] if mode == "heat" else event["start"] - end
    elif event.get("complete", event.get("t") is not None) and event.get("t") is not None:
        duration = event["t"]
        change = max(0.0, deficit(mode, event["start"], event["target"]) - allowable_deviation)
    else:
        raise ValueError("no_measured_response")
    if not _finite(duration) or duration <= 0:
        raise ValueError("invalid_observation_duration")
    if not _finite(change) or change <= 0:
        raise ValueError("no_correct_direction_response")
    return float(duration), float(change)


class _Estimator:
    """Time to get within ``allowable_deviation`` of target, with explicit fit receipts.

    The event's ``t`` is the observed time to that same endpoint, or None when
    censored. A censored target duration is independent of an observed response:
    models can fit available intervals under their source-specific equations.
    No estimator changes the BAS reference's eligibility or start/stop latches.
    """

    name = "base"

    def __init__(self, allowable_deviation: float = 1.0):
        if not _finite(allowable_deviation) or allowable_deviation < 0:
            raise ValueError("allowable_deviation must be finite and nonnegative")
        self.allowable_deviation = float(allowable_deviation)
        self.last_training_receipt: TrainingReceipt | None = None
        self.last_prediction_reason = "not_requested"

    def required_gap(self, mode: str, temp: float, target: float) -> float:
        return max(0.0, deficit(mode, temp, target) - self.allowable_deviation)

    def predict(self, mode: str, temp: float, target: float, oat: float,
                post_weekend: bool = False) -> float | None:
        if mode not in ("heat", "cool") or not all(_finite(x) for x in (temp, target)):
            self.last_prediction_reason = "invalid_input"
            return None
        if self.required_gap(mode, temp, target) == 0:
            self.last_prediction_reason = "at_assessment_endpoint"
            return 0.0
        self.last_prediction_reason = "untrained"
        try:
            result = self._predict(mode, float(temp), float(target), oat, post_weekend)
        except (ZeroDivisionError, ValueError, OverflowError):
            self.last_prediction_reason = "undefined_prediction"
            return None
        if result is None:
            return None
        if not _finite(result) or result < 0:
            self.last_prediction_reason = "invalid_model_prediction"
            return None
        self.last_prediction_reason = "predicted"
        return float(result)

    def update(self, event: Mapping[str, Any]) -> TrainingReceipt:
        # The documented API accepts any trajectory iterable. Materialize once
        # before validation so a generator is not exhausted before fitting.
        copied = dict(event)
        try:
            copied["traj"] = tuple(_trajectory(event))
        except (ValueError, TypeError, OverflowError):
            return self._receipt(event, False, "invalid_trajectory")
        return self._update(copied)

    def retry_rejected(self, event: Mapping[str, Any],
                       previous_receipt: TrainingReceipt | Mapping[str, Any]) -> TrainingReceipt:
        """Research data flow: fit only if this episode has not already fitted.

        The caller retains the identity and original native-eligibility time of
        the same episode. This operation never invokes the native BAS learner.
        Pass its returned receipt onward if evidence arrives in several stages.
        """
        previous = self._previous_receipt(previous_receipt)
        if previous["accepted"] or previous.get("details", {}).get("episode_fit_accepted", False):
            return self._receipt(event, False, "already_fitted_for_episode",
                                 previous.get("parameters", {}), retry=True,
                                 episode_fit_accepted=True, fit_performed=False)
        return self._retry_receipt(self.update(event))

    def _previous_receipt(self, receipt: TrainingReceipt | Mapping[str, Any]) -> dict[str, Any]:
        previous = receipt.as_dict() if isinstance(receipt, TrainingReceipt) else dict(receipt)
        if previous.get("model") != self.name:
            raise ValueError("a retry requires the same model's earlier receipt")
        return previous

    def _retry_receipt(self, receipt: TrainingReceipt) -> TrainingReceipt:
        details = {**receipt.details, "retry": True,
                   "episode_fit_accepted": receipt.accepted, "fit_performed": receipt.accepted}
        retried = TrainingReceipt(receipt.model, receipt.mode, receipt.accepted,
                                  receipt.reason, receipt.parameters, details)
        self.last_training_receipt = retried
        return retried

    def _receipt(self, event: Mapping[str, Any], accepted: bool, reason: str,
                 parameters: dict[str, Any] | None = None, **details: Any) -> TrainingReceipt:
        receipt = TrainingReceipt(self.name, event.get("mode"), accepted, reason,
                                  parameters or {}, details)
        self.last_training_receipt = receipt
        return receipt

    def _event_problem(self, event: Mapping[str, Any]) -> str | None:
        if event.get("mode") not in ("heat", "cool"):
            return "invalid_mode"
        if not all(_finite(event.get(key)) for key in ("start", "target")):
            return "nonfinite_temperature"
        try:
            _trajectory(event)
        except (ValueError, TypeError, OverflowError):
            return "invalid_trajectory"
        return None


class _WindowEstimator(_Estimator):
    def __init__(self, window: int = 8, allowable_deviation: float = 1.0):
        super().__init__(allowable_deviation)
        if not isinstance(window, int) or window <= 0:
            raise ValueError("window must be a positive integer")
        self.window = window

    def _store(self, histories: dict[str, list[float]], mode: str, value: float) -> None:
        histories[mode] = (histories[mode] + [float(value)])[-self.window:]


class PNNLModel1(_WindowEstimator):
    """Johnson quadratic: t = a * gap^2 + b; b is first-degree elapsed time."""

    name = "pnnl_m1_quadratic"

    def __init__(self, window: int = 8, allowable_deviation: float = 1.0):
        super().__init__(window, allowable_deviation)
        self.a = {"heat": [], "cool": []}
        self.b = {"heat": [], "cool": []}

    def _predict(self, mode, temp, target, oat, post_weekend):
        if not self.a[mode]:
            return None
        gap = self.required_gap(mode, temp, target)
        return pnnl_ema(self.a[mode]) * gap ** 2 + pnnl_ema(self.b[mode])

    def _update(self, event: Mapping[str, Any]) -> TrainingReceipt:
        problem = self._event_problem(event)
        if problem:
            return self._receipt(event, False, problem)
        try:
            duration, change = _observed_response(event, self.allowable_deviation)
        except ValueError as exc:
            return self._receipt(event, False, str(exc))
        mode = event["mode"]
        gap = self.required_gap(mode, event["start"], event["target"])
        if gap == 0:
            return self._receipt(event, False, "undefined_initial_fit_gap")
        b = minutes_per_first_degree(event)
        if b is None:
            return self._receipt(event, False, "first_degree_not_observed")
        a = (duration - b) / gap ** 2 if duration - b >= 1 else duration / (10 * change)
        if not all(_finite(x) and x > 0 for x in (a, b)):
            return self._receipt(event, False, "nonpositive_or_nonfinite_coefficient")
        self._store(self.a, mode, a)
        self._store(self.b, mode, b)
        complete = bool(event.get("complete", event.get("t") is not None))
        return self._receipt(event, True, "fitted" if complete else "fitted_partial_curve",
                             {"a": a, "b": b}, required_gap=gap,
                             observed_duration_minutes=duration, observed_change_f=change,
                             complete=complete, fit_quantity="observed_interval_coefficients",
                             initial_gap_denominator=True, target_duration_inferred=False)


class PNNLModel2(_WindowEstimator):
    """Carrier OAT-ratio model, using the supplied code's 0 F / 100 F references."""

    name = "pnnl_m2_oat_ratio"

    def __init__(self, window: int = 8, allowable_deviation: float = 1.0,
                 oat_ref_heat: float = 0.0, oat_ref_cool: float = 100.0):
        super().__init__(window, allowable_deviation)
        self.rate = {"heat": [], "cool": []}
        self.oat = {"heat": [], "cool": []}
        self.references = {"heat": oat_ref_heat, "cool": oat_ref_cool}

    def _predict(self, mode, temp, target, oat, post_weekend):
        if not self.rate[mode]:
            return None
        if not _finite(oat):
            self.last_prediction_reason = "nonfinite_outdoor_temperature"
            return None
        oat = float(oat)
        reference = self.references[mode]
        previous_oat = pnnl_ema(self.oat[mode])
        # Keep the source equation; report singular/nonphysical extrapolations
        # instead of silently clipping the ratio or inventing a replacement.
        if reference == previous_oat or reference == oat:
            self.last_prediction_reason = "undefined_outdoor_ratio"
            return None
        ratio = (reference - previous_oat) / (reference - oat)
        return self.required_gap(mode, temp, target) / pnnl_ema(self.rate[mode]) * ratio

    def _update(self, event: Mapping[str, Any]) -> TrainingReceipt:
        problem = self._event_problem(event)
        if problem:
            return self._receipt(event, False, problem)
        try:
            duration, change = _observed_response(event, self.allowable_deviation)
        except ValueError as exc:
            return self._receipt(event, False, str(exc))
        oat = event.get("oat_mean", event.get("oat"))
        if oat is None:
            oat = event.get("oat")
        if not _finite(oat):
            return self._receipt(event, False, "nonfinite_outdoor_temperature")
        mode = event["mode"]
        rate = change / duration
        if not _finite(rate) or rate <= 0:
            return self._receipt(event, False, "nonpositive_or_nonfinite_rate")
        self._store(self.rate, mode, rate)
        self._store(self.oat, mode, float(oat))
        complete = bool(event.get("complete", event.get("t") is not None))
        return self._receipt(event, True, "fitted" if complete else "fitted_partial_rate",
                             {"rate": rate, "oat": float(oat)},
                             observed_duration_minutes=duration, observed_change_f=change,
                             complete=complete, fit_quantity="observed_rate", target_duration_inferred=False)


class PNNLModel3(_WindowEstimator):
    """Siemens source adaptation, including its asymmetric heat/cool fitting.

    Cooling uses the observed-interval mean minutes/degree; heating uses the first
    degree. The supplied source never changes adjust_time, so neither do we.
    An arrival_error is never manufactured from a nonnegative deficit.
    """

    name = "pnnl_m3_regression"

    def __init__(self, window: int = 8, allowable_deviation: float = 1.0):
        super().__init__(window, allowable_deviation)
        self.a = {"heat": [], "cool": []}  # minutes/degree (source stores hours)
        self.b = {"heat": [], "cool": []}
        self.adjust_time = 0.0

    @staticmethod
    def load(mode: str, target: float, oat: float) -> float:
        return target - oat if mode == "heat" else oat - target

    def _predict(self, mode, temp, target, oat, post_weekend):
        if not self.a[mode]:
            return None
        if not _finite(oat):
            self.last_prediction_reason = "nonfinite_outdoor_temperature"
            return None
        oat = float(oat)
        gap = self.required_gap(mode, temp, target)
        load = max(0.0, self.load(mode, target, oat))
        return pnnl_ema(self.a[mode]) * gap + pnnl_ema(self.b[mode]) * gap * load / 10 + self.adjust_time

    def _update(self, event: Mapping[str, Any]) -> TrainingReceipt:
        problem = self._event_problem(event)
        if problem:
            return self._receipt(event, False, problem)
        try:
            duration, change = _observed_response(event, self.allowable_deviation)
        except ValueError as exc:
            return self._receipt(event, False, str(exc))
        if not _finite(event.get("oat")):
            return self._receipt(event, False, "nonfinite_outdoor_temperature")
        first_degree = minutes_per_first_degree(event)
        mode = event["mode"]
        if mode == "heat" and first_degree is None:
            return self._receipt(event, False, "first_degree_not_observed")
        gap = self.required_gap(mode, event["start"], event["target"])
        if gap == 0:
            return self._receipt(event, False, "undefined_initial_fit_gap")
        load = self.load(mode, event["target"], event["oat"])
        if load == 0:
            return self._receipt(event, False, "undefined_weather_coefficient")
        a = first_degree if mode == "heat" else duration / change
        b = (duration - a * gap) * 10 / (load * gap)
        if not _finite(a) or not _finite(b) or a <= 0:
            return self._receipt(event, False, "nonpositive_or_nonfinite_coefficient")
        clipped = b <= 0
        b = max(0.0, b)  # This coefficient constraint is in the supplied source.
        self._store(self.a, mode, a)
        self._store(self.b, mode, b)
        complete = bool(event.get("complete", event.get("t") is not None))
        return self._receipt(event, True, "fitted" if complete else "fitted_partial_curve",
                             {"a": a, "b": b, "adjust_time": self.adjust_time},
                             first_degree=first_degree, b_clipped_to_zero=clipped,
                             arrival_feedback_used=False, observed_duration_minutes=duration,
                             observed_change_f=change, complete=complete,
                             fit_quantity="observed_interval_coefficients",
                             initial_gap_denominator=True, target_duration_inferred=False)


def _decay_fit(errors: list[float], intervals: list[float]) -> tuple[float, str]:
    """Fit e_next = e_previous * exp(-lambda * actual_elapsed_minutes)."""
    sxy = sum(left * right for left, right in zip(errors, errors[1:]))
    sxx = sum(value ** 2 for value in errors[:-1])
    if sxy <= 0 or sxx <= 0:
        raise ValueError("nonpositive_error_products")
    if all(interval == intervals[0] for interval in intervals):
        c_step = max(0.001, min(0.999, sxy / sxx))
        return c_step ** (1 / intervals[0]), "lagged_least_squares_fixed_cadence"

    # The source assumes one-minute samples. For irregular samples, a single
    # nth-root of an average interval is not least squares for the observations.
    # Fit one continuous decay constant at their actual elapsed intervals.
    mean_interval = statistics.mean(intervals)
    low = -math.log(0.999) / mean_interval
    high = -math.log(0.001) / mean_interval

    def objective(rate: float) -> float:
        return sum((right - left * math.exp(-rate * dt)) ** 2
                   for left, right, dt in zip(errors, errors[1:], intervals))

    # Profile a bounded scalar fit before refining the best interval. These are
    # numerical fitting bounds translated from the source's per-sample bounds.
    grid = [low * (high / low) ** (i / 64) for i in range(65)]
    best = min(range(len(grid)), key=lambda i: objective(grid[i]))
    left, right = grid[max(0, best - 1)], grid[min(64, best + 1)]
    golden = (math.sqrt(5) - 1) / 2
    c, d = right - golden * (right - left), left + golden * (right - left)
    for _ in range(90):
        if objective(c) < objective(d):
            right, d = d, c
            c = right - golden * (right - left)
        else:
            left, c = c, d
            d = left + golden * (right - left)
    rate = min((low, high, (left + right) / 2), key=objective)
    return math.exp(-rate), "lagged_least_squares_actual_intervals"


class PNNLModel4(_WindowEstimator):
    """Sbs first-order error decay with an explicit conversion to minutes."""

    name = "pnnl_m4_exponential"

    def __init__(self, window: int = 8, allowable_deviation: float = 1.0,
                 earliest: float = 180.0, latest: float = 10.0):
        super().__init__(window, allowable_deviation)
        if allowable_deviation <= 0:
            raise ValueError("an exponential needs a positive allowable_deviation for finite recovery time")
        if earliest + latest <= 0:
            raise ValueError("earliest + latest must be positive")
        self.c = {"heat": [], "cool": []}
        self.prior = math.exp(-1 / (earliest + latest))

    def _predict(self, mode, temp, target, oat, post_weekend):
        c = pnnl_ema(self.c[mode]) if self.c[mode] else self.prior
        return math.log(self.allowable_deviation / deficit(mode, temp, target)) / math.log(c)

    def _update(self, event: Mapping[str, Any]) -> TrainingReceipt:
        problem = self._event_problem(event)
        if problem:
            return self._receipt(event, False, problem)
        trace = _trajectory(event)
        if len(trace) < 2:
            return self._receipt(event, False, "no_observed_interval")
        errors = [deficit(event["mode"], temp, event["target"]) for _, temp in trace]
        intervals = [right[0] - left[0] for left, right in zip(trace, trace[1:])]
        try:
            c, method = _decay_fit(errors, intervals)
        except ValueError as exc:
            return self._receipt(event, False, str(exc))
        if not _finite(c) or not 0 < c < 1:
            return self._receipt(event, False, "invalid_decay_factor")
        self._store(self.c, event["mode"], c)
        return self._receipt(event, True, "fitted", {"c_per_minute": c}, method=method,
                             complete=event.get("complete", event.get("t") is not None))


class PNNLMedian(_Estimator):
    """Median of four models, with genuinely separate post-weekend training banks."""

    name = "pnnl_deployed_median_split"

    def __init__(self, window: int = 8, weekend_window: int = 4,
                 allowable_deviation: float = 1.0, cold_start_lead: float = 180.0):
        super().__init__(allowable_deviation)
        classes = (PNNLModel1, PNNLModel2, PNNLModel3, PNNLModel4)
        self.banks = {False: [cls(window, allowable_deviation) for cls in classes],
                      True: [cls(weekend_window, allowable_deviation) for cls in classes]}
        self.weekend_trained = False
        self.cold_start_lead = float(cold_start_lead)

    def _predict(self, mode, temp, target, oat, post_weekend):
        bank = bool(post_weekend and self.weekend_trained)
        predictions = [model.predict(mode, temp, target, oat, post_weekend) for model in self.banks[bank]]
        return statistics.median(self.cold_start_lead if value is None else value for value in predictions)

    def _update(self, event: Mapping[str, Any]) -> TrainingReceipt:
        bank = bool(event.get("post_weekend", False))
        copied = dict(event)
        try:
            copied["traj"] = tuple(_trajectory(event))
        except (ValueError, TypeError, OverflowError):
            return self._receipt(event, False, "invalid_trajectory", bank=bank)
        receipts = [model.update(copied) for model in self.banks[bank]]
        accepted = any(receipt.accepted for receipt in receipts)
        if bank and accepted:
            self.weekend_trained = True
        return self._receipt(event, accepted, "bank_updated" if accepted else "no_model_fit",
                             bank="post_weekend" if bank else "weekday",
                             children=[receipt.as_dict() for receipt in receipts])

    def retry_rejected(self, event: Mapping[str, Any],
                       previous_receipt: TrainingReceipt | Mapping[str, Any]) -> TrainingReceipt:
        """Retry rejected constituents without training accepted constituents twice."""
        previous = self._previous_receipt(previous_receipt)
        children = previous.get("details", {}).get("children")
        if not children:
            return self._retry_receipt(self.update(event))
        bank = bool(event.get("post_weekend", False))
        bank_name = "post_weekend" if bank else "weekday"
        if previous["details"].get("bank") != bank_name:
            raise ValueError("a retry must use the same episode's model bank")
        if len(children) != len(self.banks[bank]):
            raise ValueError("a median retry requires each constituent's earlier receipt")
        copied = dict(event)
        try:
            copied["traj"] = tuple(_trajectory(event))
        except (ValueError, TypeError, OverflowError):
            return self._receipt(event, False, "invalid_trajectory", bank=bank_name,
                                 children=children, retry=True, fit_performed=False,
                                 episode_fit_accepted=previous["accepted"]
                                 or previous.get("details", {}).get("episode_fit_accepted", False))
        receipts = [model.retry_rejected(copied, child)
                    for model, child in zip(self.banks[bank], children)]
        accepted = any(receipt.accepted for receipt in receipts)
        cumulative = any(receipt.accepted or receipt.details.get("episode_fit_accepted", False)
                         for receipt in receipts)
        if bank and cumulative:
            self.weekend_trained = True
        return self._receipt(event, accepted,
                             "rejected_children_fitted" if accepted else "no_new_child_fit",
                             bank=bank_name, children=[receipt.as_dict() for receipt in receipts],
                             retry=True, fit_performed=accepted, episode_fit_accepted=cumulative)


class LinearRateEMA(_Estimator):
    """Comparison: one degrees/minute average per mode, from observed responses."""

    name = "m0_linear_ema"

    def __init__(self, prior: float = 0.1, alpha: float = 0.2, allowable_deviation: float = 1.0):
        super().__init__(allowable_deviation)
        if not _finite(prior) or prior <= 0 or not 0 <= alpha <= 1:
            raise ValueError("prior must be positive and alpha must be in [0, 1]")
        self.rate = {"heat": float(prior), "cool": float(prior)}
        self.alpha = float(alpha)

    def _predict(self, mode, temp, target, oat, post_weekend):
        return self.required_gap(mode, temp, target) / self.rate[mode]

    def _update(self, event: Mapping[str, Any]) -> TrainingReceipt:
        problem = self._event_problem(event)
        if problem:
            return self._receipt(event, False, problem)
        try:
            duration, change = _observed_response(event, self.allowable_deviation)
        except ValueError as exc:
            return self._receipt(event, False, str(exc))
        mode = event["mode"]
        observed = change / duration
        if not _finite(observed) or observed <= 0:
            return self._receipt(event, False, "nonpositive_or_nonfinite_rate")
        self.rate[mode] += self.alpha * (observed - self.rate[mode])
        complete = bool(event.get("complete", event.get("t") is not None))
        return self._receipt(event, True, "fitted" if complete else "fitted_partial_rate",
                             {"rate": self.rate[mode], "observed_rate": observed},
                             observed_duration_minutes=duration, observed_change_f=change,
                             complete=complete, fit_quantity="observed_rate", target_duration_inferred=False)


class NativeMinutesPerDegree(_Estimator):
    """Research endpoint adapter for the Java start learner's parameter weighting.

    This is not the BAS reference. It has two recovery states, no stop learner,
    no Niagara numeric/status semantics, no schedule transitions and no latches.
    Its update assumes the harness has already supplied an eligible observation.
    Any measured positive directional response, including a tiny partial one,
    participates with alpha=1/(oldParameterMultiplier+1)=1/3 by default.
    """

    name = "native_minutes_per_degree"

    def __init__(self, prior: float = 10.0, alpha: float = 1 / 3, allowable_deviation: float = 1.0):
        super().__init__(allowable_deviation)
        if not _finite(prior) or prior < 0 or not 0 <= alpha <= 1:
            raise ValueError("prior must be nonnegative and alpha must be in [0, 1]")
        self.minutes_per_degree = {"heat": float(prior), "cool": float(prior)}
        self.alpha = float(alpha)

    def _predict(self, mode, temp, target, oat, post_weekend):
        return self.required_gap(mode, temp, target) * self.minutes_per_degree[mode]

    def _update(self, event: Mapping[str, Any]) -> TrainingReceipt:
        problem = self._event_problem(event)
        if problem:
            return self._receipt(event, False, problem)
        trace = _trajectory(event)
        mode = event["mode"]
        if trace:
            elapsed, end = trace[-1]
            change = end - event["start"] if mode == "heat" else event["start"] - end
        elif event.get("complete", event.get("t") is not None) and event.get("t") is not None:
            elapsed = event["t"]
            change = self.required_gap(mode, event["start"], event["target"])
        else:
            return self._receipt(event, False, "no_measured_response")
        if not _finite(elapsed) or elapsed <= 0:
            return self._receipt(event, False, "invalid_observation_duration")
        if not _finite(change) or change <= 0:
            return self._receipt(event, False, "no_correct_direction_response")
        observed = elapsed / change
        previous = self.minutes_per_degree[mode]
        self.minutes_per_degree[mode] = previous + self.alpha * (observed - previous)
        return self._receipt(event, True, "fitted", {"minutes_per_degree": self.minutes_per_degree[mode],
                             "observed_minutes_per_degree": observed}, observed_change=change,
                             complete=event.get("complete", event.get("t") is not None))


class G36RecoveryLearner(_Estimator):
    """Legacy comparison inspired by the old v7 rule; not an official G36 algorithm."""

    name = "g36_inspired_legacy"

    def __init__(self, prior: float = 0.1, alpha: float = 0.5, safety: float = 1.25,
                 buffer: float = 15.0, maximum: float = 120.0, allowable_deviation: float = 1.0):
        super().__init__(allowable_deviation)
        self.rate = {"heat": float(prior), "cool": float(prior)}
        self.alpha, self.safety, self.buffer, self.maximum = alpha, safety, buffer, maximum

    def _predict(self, mode, temp, target, oat, post_weekend):
        if self.rate[mode] <= 0:
            return self.maximum
        return min(self.maximum, self.safety * self.required_gap(mode, temp, target) / self.rate[mode] + self.buffer)

    def _update(self, event: Mapping[str, Any]) -> TrainingReceipt:
        problem = self._event_problem(event)
        if problem:
            return self._receipt(event, False, problem)
        trace = _trajectory(event)
        if len(trace) < 2:
            return self._receipt(event, False, "no_observed_interval")
        mode = event["mode"]
        sign = 1 if mode == "heat" else -1
        for (t0, temp0), (t1, temp1) in zip(trace, trace[1:]):
            observed = sign * (temp1 - temp0) / (t1 - t0)
            self.rate[mode] += self.alpha * (observed - self.rate[mode])
        return self._receipt(event, True, "fitted", {"rate": self.rate[mode]}, intervals=len(trace) - 1)


def default_models(allowable_deviation: float = 1.0) -> dict[str, _Estimator]:
    """Fresh, independent estimators for an event replay or an IoT driver."""
    classes = (PNNLModel1, PNNLModel2, PNNLModel3, PNNLModel4, PNNLMedian,
               LinearRateEMA, NativeMinutesPerDegree, G36RecoveryLearner)
    return {cls.name: cls(allowable_deviation=allowable_deviation) for cls in classes}
