"""Matched official-simulator experiments; optional simulator imports are lazy.

This is a simulator adapter, not Niagara plant code. See docs/simulator.md.
No sibling controller, simulator source, scenario or results file is modified.
"""
from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor, as_completed
from collections import defaultdict
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
import gzip
import hashlib
import json
import math
import os
from pathlib import Path
import re
import sys
import tempfile
import time
import traceback
import uuid
from zoneinfo import ZoneInfo

from .models import default_models
from .reference import (Config, Inputs, OptimizedStartStop, ResearchOptimizedStartStop,
                        SOURCE_SHA256, START_IN_PROCESS, TimeAdapter, java_int)
from .sampling import ZoneSampler
from .replay import ResearchSelector, assess_event

ADAPTER_VERSION = "official-pid-water-native-ahu-v1"
SIMULATOR_RECIRCULATION_CAP = 0.7
ASSESSMENT_DEVIATION_F = 1.0
FULL_HORIZON_STEPS = 8640


def _clean(value):
    if isinstance(value, float) and not math.isfinite(value):
        return "NaN" if math.isnan(value) else ("Infinity" if value > 0 else "-Infinity")
    if isinstance(value, (datetime, Path)):
        return str(value)
    if isinstance(value, dict):
        return {str(key): _clean(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_clean(item) for item in value]
    return value


def _digest(value) -> str:
    return hashlib.sha256(json.dumps(_clean(value), sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _tree_hash(root: Path, files) -> str:
    return _digest({str(path.relative_to(root)).replace("\\", "/"): _file_hash(path)
                    for path in sorted(files)})


def _atomic_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as stream:
        json.dump(_clean(value), stream, allow_nan=False, sort_keys=True, indent=2)
        stream.write("\n")
    os.replace(temporary, path)


def _can_resume(receipt, signature, steps):
    if not (receipt and receipt.get("signature") == signature and receipt.get("status") == "complete"
            and receipt.get("steps_completed") == steps):
        return False
    history = Path(receipt.get("history_path", ""))
    return history.is_file() and receipt.get("history_sha256") == _file_hash(history)


def discover_scenarios(kit) -> list[dict]:
    """Discover actual shipped training scenarios without importing the simulator."""
    kit = Path(kit).expanduser().resolve()
    base = kit / "smart_buildings" / "training_scenarios"
    return [{"scenario_id": path.parent.parent.name + "/" + path.parent.name,
             "building": path.parent.parent.name, "weather": path.parent.name,
             "config_path": str(path), "scenario_path": str(path.parent)}
            for path in sorted(base.glob("*/*/config.gin"))]


def available_policies() -> tuple[str, ...]:
    return ("native", "winner", *default_models())


def next_schedule_event(schedule, timestamp):
    """Next actual comfort-mode transition, including weekends and holidays.

    The schedule object owns timezone interpretation. Minute probes locate its
    next hour-boundary transition; this is not a reconstructed weekday rule.
    """
    current = bool(schedule.is_comfort_mode(timestamp))
    probe = timestamp.floor("min") + timedelta(minutes=1)
    # Shipped schedules have workdays. A bounded failure is preferable to
    # inventing an event when custom schedules never transition.
    for _ in range(370 * 24 * 60):
        value = bool(schedule.is_comfort_mode(probe))
        if value != current:
            return probe, value
        probe += timedelta(minutes=1)
    raise ValueError("The supplied simulator schedule has no transition within 370 days")


def classify_geometry(room_dict, exterior_walls, *, exterior_wall_value=-2):
    """Classify explicit room coordinates by touching processed exterior walls.

    Room identifiers are lookup keys only. Four-neighbor adjacency to the
    simulator's processed wall mask determines exposure; no identifier parsing.
    """
    import numpy as np
    walls = np.asarray(exterior_walls) == exterior_wall_value
    adjacent = walls.copy()
    adjacent[1:, :] |= walls[:-1, :]
    adjacent[:-1, :] |= walls[1:, :]
    adjacent[:, 1:] |= walls[:, :-1]
    adjacent[:, :-1] |= walls[:, 1:]
    labels, evidence = {}, {}
    for room, coordinates in room_dict.items():
        points = np.asarray(coordinates, dtype=np.intp)
        if not len(points):
            labels[room] = "unknown"
            evidence[room] = {"reason": "empty_geometry"}
            continue
        exposed = int(np.count_nonzero(adjacent[points[:, 0], points[:, 1]]))
        labels[room] = "exterior" if exposed else "interior"
        evidence[room] = {"room_cells": len(points), "exterior_adjacent_cells": exposed}
    return labels, {"method": "room_coordinates_adjacent_to_processed_exterior_wall_4_neighbors",
                    "exterior_wall_value": exterior_wall_value, "rooms": evidence}


def _prepare_environment(kit: Path, scenario: dict):
    """Read-only kit load; mutable/cache/generated paths go to TEMP or output."""
    os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "hvac-optimal-mpl"))
    os.environ.setdefault("NUMBA_CACHE_DIR", str(Path(tempfile.gettempdir()) / "hvac-optimal-numba"))
    os.environ.setdefault("PYTHONPYCACHEPREFIX", str(Path(tempfile.gettempdir()) / "hvac-optimal-pycache"))
    sys.pycache_prefix = os.environ["PYTHONPYCACHEPREFIX"]
    if str(kit) not in sys.path:
        sys.path.insert(0, str(kit))
    import numpy as np
    # The upstream internal loader permits pickle. Preflight the exact files
    # with pickle disabled BEFORE any upstream loader can consume them.
    scenario_path = Path(scenario["scenario_path"])
    for filename in ("floor_plan.npy", "zone_map.npy"):
        array = np.load(scenario_path / filename, allow_pickle=False)
        if array.dtype.hasobject or array.ndim != 2:
            raise ValueError(f"Unsupported numeric geometry: {scenario_path / filename}")
    from smart_buildings.evaluate import load_hybrid_environment, create_building_meta_data
    text = Path(scenario["config_path"]).read_text(encoding="utf-8")
    text = re.sub(r"(['\"])(smart_buildings/[^'\"\r\n]+)\1",
                  lambda match: repr((kit / match.group(2)).as_posix()), text)
    text = re.sub(r"(?m)^metrics_path\s*=.*$", "metrics_path = None", text)
    with tempfile.TemporaryDirectory(prefix="hvac-simulator-config-") as temporary:
        config = Path(temporary) / "config.gin"
        config.write_text(text, encoding="utf-8")
        env = load_hybrid_environment(config)
    env.metrics_path = None
    env._occupancy_normalization_constant = 125.0
    metadata = create_building_meta_data(env, scenario_path)
    return env, metadata


def _plant_class():
    from smart_buildings.baselines.pid_plus import PIDWaterResetPolicy

    class MatchedPIDPlant(PIDWaterResetPolicy):
        """Common PID plant; native AHU schedule/command adapter around it."""
        def __init__(self, *args, **kwargs):
            self.allowed = {}
            self.forced_start = {}
            self.current_timestamp = None
            self.prestart = False
            self.comfort_active = False
            super().__init__(*args, **kwargs)

        def _get_hour_and_day(self, obs):
            local = self.current_timestamp
            if local is None:
                return super()._get_hour_and_day(obs)
            # All non-prestarting unoccupied AHUs are masked. For the enabled
            # subset, feed the unchanged PID the occupied comfort window.
            if self.comfort_active:
                return self.morning_start_hour, 0
            return self.evening_start_hour, 0

        def _ahu_error(self, obs, ctrl, low, high):
            if not self.allowed.get(ctrl["ahu_id"], False):
                return 0.0
            return super()._ahu_error(obs, ctrl, low, high)

        def _heating_shortfall(self, obs, low, high):
            enabled = [ctrl for ctrl in self.ahu_controllers if self.allowed.get(ctrl["ahu_id"], False)]
            original = self.ahu_controllers
            self.ahu_controllers = enabled
            try:
                return super()._heating_shortfall(obs, low, high)
            finally:
                self.ahu_controllers = original

        def get_action(self, obs):
            action = super().get_action(obs)
            continuous, discrete = action["continuous_action"], action["discrete_action"]
            for ctrl in self.ahu_controllers:
                ahu = ctrl["ahu_id"]
                if not self.allowed.get(ahu, False):
                    discrete[ctrl["run_discrete_idx"]] = 0
                    for index in (ctrl["temp_idx"], ctrl["pressure_idx"]):
                        if index is not None:
                            continuous[index] = -1.0
                    for _vav, _obs, actions in ctrl["zones"]:
                        for index in actions.values():
                            continuous[index] = -1.0
                    if ctrl.get("recirc_idx") is not None:
                        continuous[ctrl["recirc_idx"]] = 1.0
                elif self.forced_start.get(ahu, False):
                    discrete[ctrl["run_discrete_idx"]] = 1
                    if ctrl.get("recirc_idx") is not None:
                        continuous[ctrl["recirc_idx"]] = 1.0
            any_run = any(discrete[ctrl["run_discrete_idx"]] for ctrl in self.ahu_controllers)
            if 0 <= self.water_discrete_idx < self.n_discrete:
                discrete[self.water_discrete_idx] = int(any_run)
            if self.water_pressure_idx is not None:
                continuous[self.water_pressure_idx] = 1.0 if any_run else -1.0
            if not any_run and self.water_temp_idx is not None:
                continuous[self.water_temp_idx] = -1.0
            return action
    return MatchedPIDPlant


def _fahrenheit(kelvin):
    return (float(kelvin) - 273.15) * 1.8 + 32.0


class _AHUExperiment:
    """Independent native controller, shadows and metric history for one AHU."""
    def __init__(self, ahu, sampler, config, policy, station_timezone, write):
        self.ahu, self.sampler, self.config, self.policy = ahu, sampler, config, policy
        self.models = default_models(allowable_deviation=ASSESSMENT_DEVIATION_F)
        self.metrics = {name: {"absolute_error_sum": 0.0, "assessed": 0, "unassessed": 0,
                               "unsupported": 0, "common_assessed": 0, "common_absolute_error_sum": 0.0}
                        for name in ("native_endpoint_adapter", *self.models)}
        self.pending = None
        self.write = write
        self.now = None
        self.last_cooling = False
        self.post_weekend = False
        self.learning_events = 0
        self.training_accepted = 0
        self.command_predictions = 0
        self.last_predictions = {}
        self.last_selection = "native"
        self.error_histories = defaultdict(lambda: defaultdict(list))
        self.selector = ResearchSelector(window=8, minimum_history=1)
        if isinstance(station_timezone, str):
            station_timezone = ZoneInfo(station_timezone)
        kwargs = dict(config=config, time_adapter=TimeAdapter(station_timezone))
        if policy == "native":
            self.controller = OptimizedStartStop(**kwargs)
        else:
            self.controller = ResearchOptimizedStartStop(**kwargs, lead_predictor=self._predict_lead)

    def _mode_target(self, temp):
        return ("cool", self.config.upper_comfort_limit) if temp > self.config.upper_comfort_limit else ("heat", self.config.lower_comfort_limit)

    def _predictions(self, temp, oat, state):
        mode, target = self._mode_target(temp)
        gap = max(0.0, (temp - target if mode == "cool" else target - temp) - ASSESSMENT_DEVIATION_F)
        coefficient = getattr(state, "runtime_per_degree_cooling" if mode == "cool" else "runtime_per_degree_heating")
        predictions = {"native_endpoint_adapter": 0.0 if gap == 0 else float(1 + java_int(gap * coefficient))}
        for name, model in self.models.items():
            predictions[name] = model.predict(mode, temp, target, oat, post_weekend=self.post_weekend)
        return predictions

    def _predict_lead(self, kind, inputs, state, default_lead):
        if kind == "stop":
            return default_lead  # Identical native stop in every research arm.
        predictions = self._predictions(inputs.space_temp, inputs.outside_temp, state)
        selected = self.policy
        selection_history = None
        if selected == "winner":
            mode, _target = self._mode_target(inputs.space_temp)
            history = self.error_histories[(mode, self.post_weekend)]
            selection_history = self.selector.choose({name: predictions[name] for name in self.models}, history)
            selected = selection_history["model"] or "native"
        prediction = predictions.get(selected)
        fallback = selected != "native" and prediction is None
        lead = default_lead if selected == "native" or fallback else java_int(prediction)
        self.last_selection, self.last_predictions = ("native" if fallback else selected), predictions
        self.command_predictions += 1
        self.write({"type": "prediction", "ahu_id": self.ahu, "time": self.now,
                    "policy": self.policy, "selected": self.last_selection,
                    "fallback_reason": "selected_model_unsupported" if fallback else None,
                    "native_lead_minutes": default_lead, "command_lead_minutes": lead,
                    "endpoint_deviation_f": ASSESSMENT_DEVIATION_F, "predictions": predictions,
                    "selection_history": selection_history,
                    "metrics_before_outcome": self.metrics})
        return lead

    def _finish(self, *, native_event=None, reason):
        pending = self.pending
        if pending is None:
            return
        mode, target = pending["mode"], pending["target"]
        event = assess_event({"mode": mode, "start": pending["start"], "target": target,
                              "oat": pending["oat"], "traj": pending["traj"],
                              "post_weekend": pending["post_weekend"],
                              "source_complete": bool(native_event and native_event.get("target_reached"))},
                             ASSESSMENT_DEVIATION_F)
        observed, complete = event["t"], event["complete"]
        common = complete and all(pending["predictions"].get(name) is not None for name in self.models)
        censoring = reason in ("run_horizon", "run_horizon_censored", "next_scheduled_unoccupancy_censored", "new_start_before_previous_assessment")
        if not pending.get("assessment_done") and (complete or censoring):
            if common:
                history = self.error_histories[(mode, pending["post_weekend"])]
                for name in self.models:
                    history[name].append(pending["predictions"][name] - observed)
            for name, prediction in pending["predictions"].items():
                metric = self.metrics[name]
                if prediction is None:
                    metric["unsupported"] += 1
                elif not complete:
                    metric["unassessed"] += 1
                else:
                    error = abs(prediction - observed)
                    metric["absolute_error_sum"] += error
                    metric["assessed"] += 1
                    if common:
                        metric["common_assessed"] += 1
                        metric["common_absolute_error_sum"] += error
            self.write({"type": "outcome", "ahu_id": self.ahu, "time": self.now,
                        "reason": reason, "research_event": event,
                        "endpoint": "first_observed_within_1F", "interpolation": False,
                        "assessment_window": "start_command_through_next_scheduled_unoccupancy_or_run_horizon",
                        "common_cohort": common,
                        "native_endpoint_adapter": "derived_1F_forecast_not_native_command_lead",
                        "predictions_before_outcome": pending["predictions"],
                        "metrics_after_outcome": self.metrics})
            pending["assessment_done"] = True
        if native_event is not None:
            pending["native_eligibility"] = native_event
            self.write({"type": "native_observation", "ahu_id": self.ahu, "time": self.now,
                        "native_observation": native_event, "research_event": event})
        eligibility = pending.get("native_eligibility")
        if native_event is not None or (complete and eligibility is not None and not pending.get("assessment_done_before_fit")):
            # Scoring stops at the shared endpoint; source-based fitting uses
            # all actually observed native-eligible response intervals.
            training_event = {**event, "traj": tuple(pending["traj"])}
            previous_receipts = pending.setdefault("fit_receipts", {})
            receipts = {}
            for name, model in self.models.items():
                previous = previous_receipts.get(name)
                receipt = (model.retry_rejected(training_event, previous) if previous is not None
                           else model.update(training_event)).as_dict()
                receipts[name] = receipt
                previous_receipts[name] = receipt
                self.training_accepted += int(receipt["accepted"])
            self.write({"type": "native_training" if native_event is not None else "deferred_research_training",
                        "ahu_id": self.ahu, "time": self.now, "native_eligible": True,
                        "native_observation": eligibility, "research_event": training_event,
                        "training_receipts": receipts,
                        "fit_policy": "accepted_once_per_model_per_native_eligible_episode_retry_rejections_at_endpoint"})
            pending["native_training_done"] = True
            pending["assessment_done_before_fit"] = complete
        if censoring or (pending.get("assessment_done") and
                         (pending.get("native_training_done") or self.controller.state.program_mode != START_IN_PROCESS)):
            self.pending = None

    def tick(self, inputs, now, *, post_weekend=None):
        self.now = now
        self.post_weekend = now.weekday() == 0 if post_weekend is None else bool(post_weekend)
        if self.pending is not None:
            elapsed = (now - self.pending["time"]).total_seconds() / 60
            self.pending["traj"].append((elapsed, inputs.space_temp))
            self.pending["occupation_seen"] = self.pending.get("occupation_seen", False) or inputs.schedule_status
        result = self.controller.tick(inputs, now=now)
        for event in result.events:
            if event["type"] == "native_learning":
                self.learning_events += 1
                if event["kind"] == "start":
                    self._finish(native_event=event, reason="native_eligible_observation")
            elif event["type"] == "trigger" and event["kind"] == "start":
                if self.pending is not None:
                    self._finish(reason="new_start_before_previous_assessment")
                mode, target = self._mode_target(inputs.space_temp)
                predictions = self._predictions(inputs.space_temp, inputs.outside_temp, result.state)
                self.pending = {"time": now, "mode": mode, "target": target,
                                "start": inputs.space_temp, "oat": inputs.outside_temp,
                                "post_weekend": self.post_weekend, "traj": [(0.0, inputs.space_temp)],
                                "predictions": predictions}
                self.write({"type": "assessment_prediction", "ahu_id": self.ahu, "time": now,
                            "endpoint": "first_observed_within_1F", "predictions": predictions})
        if self.pending is not None:
            if self.pending.get("occupation_seen") and not inputs.schedule_status:
                self._finish(reason="next_scheduled_unoccupancy_censored")
            else:
                self._finish(reason="endpoint_observed")
        return result

    def finish_horizon(self, space_temp, now):
        """Assess the final returned simulator sample without a native tick.

        This may complete a research endpoint or a deferred research fit from
        an already native-eligible episode. It never invokes controller.tick,
        creates native eligibility, or issues another plant action.
        """
        self.now = now
        if self.pending is not None:
            elapsed = (now - self.pending["time"]).total_seconds() / 60
            if elapsed > self.pending["traj"][-1][0]:
                self.pending["traj"].append((elapsed, space_temp))
        self.write({"type": "terminal_research_observation", "ahu_id": self.ahu,
                    "time": now, "space_temp": space_temp, "native_tick_performed": False,
                    "plant_action_performed": False})
        self._finish(reason="run_horizon")

    def summary(self):
        return {"ahu_id": self.ahu, "sampling": self.sampler.selection_receipt(),
                "native_learning_events": self.learning_events, "accepted_research_fits": self.training_accepted,
                "research_prediction_calls": self.command_predictions, "last_selected": self.last_selection,
                "metrics": {name: {**metric, "mae_minutes": metric["absolute_error_sum"] / metric["assessed"]
                                      if metric["assessed"] else None,
                                    "common_mae_minutes": metric["common_absolute_error_sum"] / metric["common_assessed"]
                                      if metric["common_assessed"] else None} for name, metric in self.metrics.items()},
                "final_native_state": self.controller.state.to_dict()}


def _run_job(job):
    started = time.perf_counter()
    attempt = Path(job["out"]) / "attempts" / (job["job_id"] + "-" + uuid.uuid4().hex)
    attempt.mkdir(parents=True)
    receipt = {**job, "attempt_path": str(attempt), "status": "running", "steps_completed": 0,
               "native_source_sha256": SOURCE_SHA256, "adapter_version": ADAPTER_VERSION}
    _atomic_json(attempt / "receipt.json", receipt)
    env = None
    try:
        env, metadata = _prepare_environment(Path(job["kit"]), job["scenario"])
        plant = _plant_class()(metadata, env.action_spec())
        schedule = env.building.simulator._hvac.schedule
        caps = {handler.device_id(): float(handler._max_recirculation)
                for handler in env.building.simulator._hvac.air_handler.ahu_zones_map}
        cap = next(iter(caps.values())) if len(set(caps.values())) == 1 else caps
        building = env.building.simulator.building
        mapped_rooms = {room for rooms in metadata["ahu_zone_assignments"].values() for room in rooms}
        labels, classification = classify_geometry({room: building.room_dict[room] for room in mapped_rooms}, building._exterior_walls)
        # This is the actual simulator relationship, not a room/VAV naming guess.
        zone_to_vavs = env.building.simulator._hvac._zone_to_vav_ids
        names = metadata["observation_field_names"]
        zone_indices = {room: [names.index(vav + "_zone_air_temperature_sensor") for vav in vavs]
                        for room, vavs in zone_to_vavs.items()}
        normalized = metadata["observation_normalization_metadata"]["zone_air_temperature_sensor"]
        lower, upper = map(_fahrenheit, schedule.comfort_temp_window)
        obs, _ = env.reset(seed=job["seed"])
        schedule_clock = schedule._localize_or_convert_timezone(env.building.current_timestamp)
        history = attempt / "ahu.jsonl.gz"
        with gzip.open(history, "wt", encoding="utf-8", newline="\n") as log:
            def write(record):
                log.write(json.dumps(_clean(record), allow_nan=False, separators=(",", ":")) + "\n")
            experiments = {}
            for ahu, rooms in metadata["ahu_zone_assignments"].items():
                sampler = ZoneSampler(ahu, rooms, fraction=job["sample_fraction"], seed=job["seed"],
                                      zone_types={room: labels.get(room, "unknown") for room in rooms},
                                      weights=(job.get("zone_weights") or {}).get(ahu))
                experiments[ahu] = _AHUExperiment(ahu, sampler, Config(lower_comfort_limit=lower, upper_comfort_limit=upper),
                                                 job["policy"], schedule_clock.tzinfo, write)
            write({"type": "job_header", "scenario": job["scenario"], "policy": job["policy"],
                   "phase": job["phase"], "signature": job["signature"],
                   "station_timezone": str(schedule.time_zone), "time_step_seconds": env.time_step_sec,
                   "effective_schedule_timezone": str(schedule_clock.tzinfo),
                   "schedule_timestamp_input_naive": env.building.current_timestamp.tzinfo is None,
                   "native_clock": "quantized_to_simulator_steps_not_one_minute_equivalence",
                   "classification": classification,
                   "comfort_window_f": [lower, upper],
                   "sampling": {ahu: experiment.sampler.selection_receipt() for ahu, experiment in experiments.items()},
                   "simulator_recirculation_cap": cap,
                   "simulator_recirculation_cap_by_ahu": caps,
                   "plant": "official_PIDWaterResetPolicy_with_explicit_schedule_command_adapter",
                   "assessment_deviation_f": ASSESSMENT_DEVIATION_F})
            reward_sum = 0.0
            cached_event = None
            ctrls = {ctrl["ahu_id"]: (index, ctrl) for index, ctrl in enumerate(plant.ahu_controllers)}
            for step in range(job["steps"]):
                timestamp = env.building.current_timestamp
                local = schedule._localize_or_convert_timezone(timestamp)
                occupied = bool(schedule.is_comfort_mode(timestamp))
                if cached_event is None or timestamp >= cached_event[0]:
                    cached_event = next_schedule_event(schedule, timestamp)
                next_time, next_value = cached_event
                next_clock = schedule._localize_or_convert_timezone(next_time)
                post_weekend = bool(next_value and not schedule.is_comfort_mode(next_time - timedelta(days=1) + timedelta(minutes=1)))
                temperatures = {room: _fahrenheit(sum(float(obs[index]) * normalized["sample_std"] + normalized["sample_mean"]
                                                      for index in indices) / len(indices))
                                for room, indices in zone_indices.items()}
                plant.current_timestamp = local
                plant.allowed, plant.forced_start = {}, {}
                for ahu, experiment in experiments.items():
                    index, ctrl = ctrls[ahu]
                    error = plant.pid_state[index]["prev_error"]
                    if error:
                        experiment.last_cooling = error < 0
                    oat = _fahrenheit(obs[ctrl["oat_idx"]])
                    inputs = Inputs(space_temp=experiment.sampler.read(temperatures), outside_temp=oat,
                                    start_enable=job["phase"] in ("start", "both"), stop_enable=job["phase"] in ("stop", "both"),
                                    schedule_status=occupied, next_event_time=next_clock.to_pydatetime(),
                                    next_event_value=next_value, heat_cool_mode=experiment.last_cooling)
                    result = experiment.tick(inputs, local.to_pydatetime(), post_weekend=post_weekend)
                    start_command, stop_command = result.state.start_time_command, result.state.stop_time_command
                    forced_start = not start_command.status_null and start_command.value
                    forced_stop = not stop_command.status_null and not stop_command.value
                    plant.allowed[ahu] = forced_start or (occupied and not forced_stop)
                    plant.forced_start[ahu] = forced_start
                    write({"type": "ahu_tick", "step": step, "ahu_id": ahu, "time": local.isoformat(),
                           "sample_temperature_f": inputs.space_temp, "outside_temperature_f": oat,
                           "selected_zone_temperatures_f": {room: temperatures[room] for room in experiment.sampler.selected_zone_ids},
                           "occupied": occupied, "allowed_run": plant.allowed[ahu], "forced_start": forced_start,
                           "post_weekend": post_weekend,
                           "post_weekend_source": "next_actual_start_follows_day_without_comfort_mode_at_start_plus_one_minute",
                           "heat_cool_mode_source": "previous_signed_PID_error_latched_heating_default",
                           **result.to_dict()})
                plant.prestart = not occupied and any(plant.forced_start.values())
                plant.comfort_active = occupied or plant.prestart
                action = plant.get_action(obs)
                obs, reward, terminated, truncated, info = env.step(action)
                reward_sum += float(reward)
                receipt["steps_completed"] = step + 1
                if terminated or truncated:
                    receipt["environment_ended"] = True
                    break
            # env.step has already returned this real final observation. Use it
            # for research assessment without an extra native action/tick.
            terminal_time = schedule._localize_or_convert_timezone(env.building.current_timestamp).to_pydatetime()
            terminal_temperatures = {
                room: _fahrenheit(sum(float(obs[index]) * normalized["sample_std"] + normalized["sample_mean"]
                                      for index in indices) / len(indices))
                for room, indices in zone_indices.items()}
            for experiment in experiments.values():
                experiment.finish_horizon(experiment.sampler.read(terminal_temperatures), terminal_time)
            receipt.update(status="complete" if receipt["steps_completed"] == job["steps"] else "incomplete",
                           total_reward=reward_sum, mean_reward=reward_sum / receipt["steps_completed"] if receipt["steps_completed"] else None,
                           score_status="full_horizon_local_raw_reward" if receipt["steps_completed"] == FULL_HORIZON_STEPS else "integration_only_not_a_competition_score",
                           time_step_seconds=env.time_step_sec, history_path=str(history),
                           simulator_recirculation_cap=cap, simulator_recirculation_cap_by_ahu=caps,
                           classification_summary={label: sum(value == label for value in labels.values()) for label in ("exterior", "interior", "unknown")},
                           ahus=[experiment.summary() for experiment in experiments.values()])
        receipt["history_sha256"] = _file_hash(history)
    except Exception:
        receipt.update(status="failed", error=traceback.format_exc())
    finally:
        if env is not None:
            try:
                env.close()
            except Exception:
                receipt.update(status="failed", close_error=traceback.format_exc())
        receipt["wall_seconds"] = time.perf_counter() - started
        _atomic_json(attempt / "receipt.json", receipt)
        _atomic_json(Path(job["out"]) / "jobs" / (job["job_id"] + ".json"), receipt)
    return receipt


def run_matrix(kit, out, *, policies=("native",), steps=FULL_HORIZON_STEPS, workers=2,
               phase="both", resume=True, limit=None, sample_fraction=0.3, seed=0,
               shard_index=None, shard_count=None, zone_weights=None) -> dict:
    """Run actual shipped scenarios with isolated per-AHU state and exact resume.

    Short runs are integration receipts, never substitute full-horizon scores.
    Different code/input/config signatures require a new output directory.
    """
    kit, out = Path(kit).expanduser().resolve(), Path(out).expanduser().resolve()
    protected = kit.parent if kit.name == ".kit" else kit
    if out.is_relative_to(protected):
        raise ValueError("Simulator outputs must be outside the supplied kit/controller checkout")
    policies = tuple(policies)
    if phase not in ("start", "stop", "both"):
        raise ValueError("phase must be start, stop, or both")
    if steps < 1 or workers < 1:
        raise ValueError("steps and workers must be positive")
    if len(set(policies)) != len(policies) or not policies or set(policies) - set(available_policies()):
        raise ValueError(f"Choose unique policies from {available_policies()!r}")
    scenarios = discover_scenarios(kit)
    if not scenarios:
        raise FileNotFoundError(f"No official training scenario configs under {kit}")
    if shard_count is not None:
        if shard_index is None or not 0 <= shard_index < shard_count:
            raise ValueError("Require 0 <= shard_index < shard_count")
        scenarios = [scenario for index, scenario in enumerate(scenarios) if index % shard_count == shard_index]
    if limit is not None:
        scenarios = scenarios[:limit]
    package = Path(__file__).resolve().parent
    kit_files = list((kit / "smart_buildings").rglob("*.py"))
    kit_files += list((kit / "smart_buildings" / "weather" / "csv").glob("*.csv"))
    for scenario in scenarios:
        kit_files.extend(Path(scenario["scenario_path"]).glob("*"))
    kit_files = [path for path in kit_files if path.is_file() and path.suffix in (".py", ".csv", ".gin", ".yaml", ".npy")]
    identity = {"adapter_version": ADAPTER_VERSION, "native_source_sha256": SOURCE_SHA256,
                "code_sha256": _tree_hash(package, package.glob("*.py")),
                "kit_input_sha256": _tree_hash(kit, set(kit_files)),
                "kit": str(kit), "policies": policies, "steps": steps, "phase": phase,
                "sample_fraction": sample_fraction, "seed": seed, "assessment_deviation_f": ASSESSMENT_DEVIATION_F,
                "zone_weights": zone_weights,
                "scenarios": [scenario["scenario_id"] for scenario in scenarios]}
    signature = _digest(identity)
    manifest_path = out / "manifest.json"
    if manifest_path.exists():
        previous = json.loads(manifest_path.read_text(encoding="utf-8"))
        if not resume or previous.get("signature") != signature:
            raise FileExistsError("Existing simulator results have a different signature or resume=False; choose a new output directory")
    elif out.exists() and any(out.iterdir()):
        raise FileExistsError("Output directory contains unrecognized files; choose a clean output directory")
    out.mkdir(parents=True, exist_ok=True)
    jobs, results = [], []
    for scenario in scenarios:
        for policy in policies:
            job_id = scenario["scenario_id"].replace("/", "--") + "--" + policy
            job = dict(job_id=job_id, signature=signature, kit=str(kit), out=str(out), scenario=scenario,
                       policy=policy, steps=steps, phase=phase, sample_fraction=sample_fraction, seed=seed,
                       zone_weights=zone_weights)
            saved = out / "jobs" / (job_id + ".json")
            existing = json.loads(saved.read_text(encoding="utf-8")) if saved.exists() else None
            if _can_resume(existing, signature, steps):
                results.append(existing)
            else:
                jobs.append(job)
    manifest = {"signature": signature, "identity": identity, "job_count": len(jobs) + len(results),
                "status": "running", "complete": len(results), "failed": 0,
                "pending": len(jobs), "results": results}
    _atomic_json(manifest_path, manifest)
    def record(receipt):
        results.append(receipt)
        manifest.update(results=results, complete=sum(item["status"] == "complete" for item in results),
                        failed=sum(item["status"] != "complete" for item in results), pending=manifest["job_count"] - len(results))
        _atomic_json(manifest_path, manifest)
    if workers == 1:
        for job in jobs:
            record(_run_job(job))
    else:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            futures = {pool.submit(_run_job, job): job for job in jobs}
            for future in as_completed(futures):
                try:
                    record(future.result())
                except Exception:
                    record({**futures[future], "status": "failed", "steps_completed": 0, "error": traceback.format_exc()})
    manifest["status"] = "complete" if not manifest["failed"] else "failed"
    _atomic_json(manifest_path, manifest)
    return manifest
