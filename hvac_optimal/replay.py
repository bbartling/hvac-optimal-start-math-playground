"""Prequential research evaluation of recorded recoveries (standard library only).

This module never changes the frozen BAS reference. A recorded fixed-schedule
trajectory is a prediction dataset, not a counterfactual closed-loop rollout.
"""
from __future__ import annotations

import csv
import gzip
import math
from collections import Counter, defaultdict
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping

from .models import TrainingReceipt, default_models


def _number(value: Any) -> float | None:
    try:
        result = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return result if math.isfinite(result) else None


def _boolean(value: Any) -> bool:
    if isinstance(value, str):
        return value.strip().lower() in {"true", "1", "yes"}
    return bool(value)


def _csv_rows(path: Path) -> list[dict[str, str]]:
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def assess_event(event: Mapping[str, Any], allowable_deviation: float = 1.0) -> dict[str, Any]:
    """Set the common endpoint from observed samples; never invent a censored time.

    ``t`` is the first observed sample within tolerance. It is intentionally not
    interpolated. ``source_complete`` describes the old exact-target label;
    ``complete`` describes this declared endpoint. Measured partial trajectories
    remain available to estimators which can fit them.
    """
    if not math.isfinite(allowable_deviation) or allowable_deviation < 0:
        raise ValueError("allowable_deviation must be finite and nonnegative")
    result = deepcopy(dict(event))
    result["source_complete"] = _boolean(event.get("source_complete", event.get("complete", False)))
    result["allowable_deviation"] = float(allowable_deviation)
    result["endpoint_time_method"] = "first_observed_sample_within_tolerance"
    result["endpoint_change_method"] = "initial_distance_minus_allowable_deviation"
    result["arrival_error"] = event.get("arrival_error")  # measured signed feedback only
    mode = event.get("mode")
    start, target = _number(event.get("start")), _number(event.get("target"))
    trace = []
    invalid = mode not in {"heat", "cool"} or start is None or target is None
    try:
        for minute, temp in event.get("traj", ()):
            minute, temp = _number(minute), _number(temp)
            if minute is None or temp is None or minute < 0 or (trace and minute <= trace[-1][0]):
                invalid = True
                break
            trace.append((minute, temp))
    except (TypeError, ValueError):
        invalid = True
    # A missing/mismatched initial sample cannot be repaired from future samples.
    if not trace or trace[0][0] != 0 or trace[0][1] != start:
        invalid = True
    result.update(t=None, complete=False, status="invalid" if invalid else "censored", traj=tuple(trace))
    if invalid:
        result["assessment_reason"] = "invalid_or_missing_start_trajectory"
        return result
    sign = 1 if mode == "heat" else -1
    for index, (minute, temp) in enumerate(trace):
        if sign * (target - temp) <= allowable_deviation:
            result.update(t=minute, complete=True, status="at_endpoint" if minute == 0 else "complete",
                          traj=tuple(trace[:index + 1]), assessment_reason="observed_endpoint")
            return result
    change = sign * (trace[-1][1] - start)
    result["status"] = "partial" if change > 0 and trace[-1][0] > 0 else "censored"
    result["assessment_reason"] = "endpoint_not_observed"
    return result


def load_recovery_events(data_dir: str | Path, allowable_deviation: float = 1.0) -> list[dict[str, Any]]:
    """Load every bundled recovery using explicit Fahrenheit/minute provenance.

    Files are paired by event ID. Their original order is retained within each
    trajectory; malformed order is reported as invalid rather than reordered.
    """
    directory = Path(data_dir)
    events = _csv_rows(directory / "recovery_events.csv.gz")
    traces: dict[str, list[tuple[Any, Any]]] = defaultdict(list)
    for row in _csv_rows(directory / "recovery_traces.csv.gz"):
        traces[row["event"]].append((row["minute"], row["temp_f"]))
    seen = set()
    normalized = []
    for row in events:
        identifier = row["event"]
        if identifier in seen:
            raise ValueError(f"duplicate recovery event ID: {identifier}")
        seen.add(identifier)
        source_time = _number(row.get("minutes_to_target"))
        event = dict(event=identifier, scenario=row["scenario"], city=row.get("city"),
                     ahu=row["ahu"], date=row["date"], mode=row["mode"],
                     post_weekend=_boolean(row["post_weekend"]), start=_number(row["start_temp_f"]),
                     target=_number(row["target_f"]), oat=_number(row["oat_f"]),
                     oat_mean=_number(row["oat_mean_f"]), traj=traces[identifier],
                     source_complete=source_time is not None, source_minutes_to_target=source_time,
                     arrival_error=None, temperature_unit="degF", time_unit="minute",
                     provenance="bundled fixed-180 simulator recovery; original exact-target label retained")
        normalized.append(assess_event(event, allowable_deviation))
    orphaned = set(traces) - seen
    if orphaned:
        raise ValueError(f"trajectory event IDs missing metadata: {sorted(orphaned)}")
    return normalized


class ResearchSelector:
    """Explicit history-only MAE selector, separate from native BAS control.

    Only past completed events assessed for every candidate enter selection
    histories. No-history produces no selection unless ``cold_start_model`` is
    explicitly supplied. Ties use candidate insertion order. There is no safety
    guard, persistence threshold, or hidden coefficient modification.
    """

    def __init__(self, window: int | None = 8, minimum_history: int = 1,
                 cold_start_model: str | None = None):
        if window is not None and (not isinstance(window, int) or window <= 0):
            raise ValueError("window must be a positive integer or None")
        if not isinstance(minimum_history, int) or minimum_history < 1:
            raise ValueError("minimum_history must be a positive integer")
        self.window, self.minimum_history, self.cold_start_model = window, minimum_history, cold_start_model

    def choose(self, predictions: Mapping[str, float | None], history: Mapping[str, list[float]]) -> dict[str, Any]:
        scores = {}
        counts = {}
        for name, prediction in predictions.items():
            values = history.get(name, [])
            values = values[-self.window:] if self.window is not None else values
            counts[name] = len(values)
            if prediction is not None and len(values) >= self.minimum_history:
                scores[name] = sum(abs(value) for value in values) / len(values)
        selected = min(scores, key=scores.get) if scores else None
        reason = "lowest_prior_common_cohort_mae" if scores else "no_eligible_history"
        if selected is None and self.cold_start_model is not None and predictions.get(self.cold_start_model) is not None:
            selected, reason = self.cold_start_model, "explicit_cold_start_model"
        return dict(model=selected, prediction=predictions.get(selected), reason=reason,
                    prior_mae=scores, prior_counts=counts, tie_policy="candidate_insertion_order")


@dataclass
class ReplayResult:
    records: list[dict[str, Any]] = field(default_factory=list)
    selection_records: list[dict[str, Any]] = field(default_factory=list)
    error_history: list[dict[str, Any]] = field(default_factory=list)

    def summary(self) -> list[dict[str, Any]]:
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for record in self.records:
            grouped[record["model"]].append(record)
        result = []
        for name, records in grouped.items():
            available = [row for row in records if row["error"] is not None]
            common = [row for row in available if row["common_cohort"]]
            mean = lambda rows, key: sum(row[key] for row in rows) / len(rows) if rows else None
            result.append(dict(model=name, events=len(records), endpoint_complete=sum(row["complete"] for row in records),
                               source_censored=sum(not row["source_complete"] for row in records),
                               endpoint_censored=sum(not row["complete"] and row["event_status"] != "invalid" for row in records),
                               invalid=sum(row["event_status"] == "invalid" for row in records),
                               at_endpoint=sum(row["event_status"] == "at_endpoint" for row in records),
                               partial=sum(row["event_status"] == "partial" for row in records),
                               assessed=len(available), unassessed=len(records) - len(available),
                               unavailable_prediction=sum(row["prediction"] is None for row in records),
                               fitted=sum(row["training"]["accepted"] for row in records),
                               mae=mean(available, "absolute_error"), bias=mean(available, "error"),
                               common_assessed=len(common), common_mae=mean(common, "absolute_error"),
                               common_bias=mean(common, "error"),
                               training_reasons=dict(Counter(row["training"]["reason"] for row in records))))
        return result


def run_replay(events: Iterable[Mapping[str, Any]], model_factory: Callable[[], Mapping[str, Any]] = default_models,
               *, max_lead: float | None = None, callback: Callable[[dict[str, Any]], None] | None = None,
               selector: ResearchSelector | None = None) -> ReplayResult:
    """Predict all candidates, observe the outcome, then train, once per event.

    Fresh models are created for each (scenario, AHU). Each estimator owns its
    heat/cool and optional post-weekend banks. Error histories are additionally
    separated by mode and post-weekend. Input order does not change date order.
    There is no default prediction clamp or imputed cold-start lead.
    """
    if max_lead is not None and (not math.isfinite(max_lead) or max_lead < 0):
        raise ValueError("max_lead must be nonnegative and finite or None")
    ordered = sorted((deepcopy(dict(event)) for event in events),
                     key=lambda row: (str(row["scenario"]), str(row["ahu"]), str(row["date"]), str(row["event"])))
    keys = [(str(row["scenario"]), str(row["ahu"]), str(row["event"])) for row in ordered]
    if len(set(keys)) != len(keys):
        raise ValueError("event identifiers must be unique within each scenario/AHU")
    result = ReplayResult()
    states: dict[tuple[str, str], Mapping[str, Any]] = {}
    histories: dict[tuple[str, str, str, bool], dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))

    def emit(message):
        if callback:
            callback(deepcopy(message))

    for event in ordered:
        group = (str(event["scenario"]), str(event["ahu"]))
        if group not in states:
            states[group] = dict(default_models(event.get("allowable_deviation", 1.0))
                                 if model_factory is default_models else model_factory())
            if not states[group]:
                raise ValueError("model_factory must return at least one estimator")
        models = states[group]
        history_key = (*group, event["mode"], bool(event.get("post_weekend", False)))
        metadata = {key: event.get(key) for key in ("event", "scenario", "ahu", "date", "city", "mode", "post_weekend")}
        predictions, raw, reasons = {}, {}, {}
        valid_event = event.get("status") != "invalid"
        # Do not reveal this event's outcome/training to any model before every prediction.
        for name, model in models.items():
            if ("allowable_deviation" in event and hasattr(model, "allowable_deviation") and
                    model.allowable_deviation != event["allowable_deviation"]):
                raise ValueError("event and model assessment tolerances must match")
            value = model.predict(event["mode"], event["start"], event["target"], event.get("oat"),
                                  bool(event.get("post_weekend", False))) if valid_event else None
            raw[name] = _number(value)
            if raw[name] is not None and raw[name] < 0:
                raw[name] = None
            predictions[name] = min(max_lead, raw[name]) if raw[name] is not None and max_lead is not None else raw[name]
            reasons[name] = getattr(model, "last_prediction_reason", "returned_prediction" if value is not None else "unavailable") if valid_event else "invalid_event"
            emit(dict(phase="prediction", model=name, raw_prediction=raw[name], prediction=predictions[name],
                      reason=reasons[name], **metadata))
        selection = selector.choose(predictions, histories[history_key]) if selector is not None else None
        if selection is not None:
            selection = dict(selection, **metadata)
            result.selection_records.append(selection)
            emit(dict(phase="selection", **selection))
        actual = _number(event.get("t")) if event.get("complete") and valid_event else None
        common = actual is not None and all(value is not None for value in predictions.values())
        emit(dict(phase="outcome", actual=actual, complete=bool(event.get("complete")),
                  event_status=event.get("status"), common_cohort=common, **metadata))
        for name, model in models.items():
            receipt = (model.update(deepcopy(event)) if valid_event else
                       TrainingReceipt(name, event.get("mode"), False, "invalid_event"))
            training = receipt.as_dict() if hasattr(receipt, "as_dict") else dict(receipt)
            prediction = predictions[name]
            error = prediction - actual if prediction is not None and actual is not None else None
            record = dict(metadata, model=name, raw_prediction=raw[name], prediction=prediction,
                          prediction_reason=reasons[name], actual=actual, complete=bool(event.get("complete")),
                          source_complete=bool(event.get("source_complete", event.get("complete"))),
                          event_status=event.get("status", "complete" if event.get("complete") else "censored"),
                          common_cohort=common, error=error, absolute_error=abs(error) if error is not None else None,
                          training=training, max_lead=max_lead)
            result.records.append(record)
            if error is not None:
                result.error_history.append(dict(metadata, model=name, error=error, absolute_error=abs(error), common_cohort=common))
            if common:
                histories[history_key][name].append(error)
            emit(dict(phase="training", model=name, training=training, **metadata))
        if selection is not None:
            selection["actual"] = actual
            selection["error"] = selection["prediction"] - actual if selection["prediction"] is not None and actual is not None else None
    return result
