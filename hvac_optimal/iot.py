"""Timestamped, hardware-neutral IoT adapter; no networking or field writes.

Each device has its own reference controller. Transport errors are explicit;
no extra operating or learning eligibility checks are applied here.
"""

from __future__ import annotations

from dataclasses import fields
from datetime import datetime
import json
from typing import Callable, Iterable, TextIO

from .reference import Config, Inputs, OptimizedStartStop, TimeAdapter
from .sampling import ZoneSampler


def _timestamp(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00")) if isinstance(value, str) else value


class IoTDriver:
    """Long-lived JSON-message driver, with independent per-device state.

    Tick timestamps are supplied by the caller. Delivering one-minute scans
    at :15 and executing command links belong to the external IO adapter.
    A callback receives notifications after each tick, not a new control gate.
    """

    def __init__(self, *, on_result: Callable[[dict], None] | None = None):
        self.controllers: dict[str, OptimizedStartStop] = {}
        self.samplers: dict[str, ZoneSampler] = {}
        self.on_result = on_result

    def process(self, message: dict) -> dict:
        device = str(message.get("device", "device"))
        event = message.get("event", "tick")
        if event == "configure":
            if device in self.controllers:
                raise ValueError("configure creates a device once; use user_parameter for native rate changes")
            config = Config(**message.get("config", {}))
            adapter = TimeAdapter()
            if "station_timezone" in message:
                from zoneinfo import ZoneInfo
                adapter.station_timezone = ZoneInfo(message["station_timezone"])
            controller = OptimizedStartStop(config, time_adapter=adapter)
            sampler = None
            if "zones" in message:
                sampler = ZoneSampler(
                    device, message["zones"], fraction=message.get("sample_fraction", 0.3),
                    seed=message.get("sample_seed", 0), weights=message.get("zone_weights"),
                    selected_zone_ids=message.get("selected_zone_ids"), zone_types=message.get("zone_types"),
                )
            self.controllers[device] = controller
            if sampler is not None:
                self.samplers[device] = sampler
            return {"device": device, "event": "configured", "state": self.controllers[device].state.to_dict()}
        if "now" not in message:
            raise ValueError("a tick/parameter message requires an explicit timestamp in now")
        now = _timestamp(message["now"])
        if device not in self.controllers:
            self.controllers[device] = OptimizedStartStop()
        controller = self.controllers[device]
        if event == "user_parameter":
            applied = controller.user_parameter_changed(
                message["name"], float(message["value"]), now=now,
                running=message.get("running", True), steady_state=message.get("steady_state", True),
            )
            result = {"device": device, "event": event, "applied": applied,
                      "state": controller.state.to_dict()}
        elif event == "tick":
            values = dict(message.get("inputs", {}))
            sampling = None
            if "zone_temperatures" in message:
                if device not in self.samplers:
                    raise ValueError("configure this device's mapped zones before sending zone temperatures")
                values["space_temp"], sampling = self.samplers[device].read(
                    message["zone_temperatures"], with_receipt=True)
            if "next_event_time" in values:
                values["next_event_time"] = _timestamp(values["next_event_time"])
            # Dataclass keyword validation is transport validation, not a new
            # BAS validity rule: Inputs still preserves every native branch.
            inputs = Inputs(**values)
            result = {"device": device, "event": event, **controller.tick(inputs, now=now).to_dict()}
            if sampling is not None:
                result["sampling"] = sampling
        else:
            raise ValueError(f"unknown message event {event!r}")
        if self.on_result is not None:
            self.on_result(json.loads(json.dumps(result)))
        return result


def run_jsonl(source: Iterable[str], destination: TextIO, *, driver: IoTDriver | None = None) -> int:
    """Consume stdin-like JSONL; output one receipt per nonempty input line.

    Malformed packets get error receipts; processing continues. No private
    source packet, exception traceback, credential or env dump is echoed.
    """
    driver = driver or IoTDriver()
    errors = 0
    for number, line in enumerate(source, 1):
        if not line.strip():
            continue
        try:
            message = json.loads(line)
            if not isinstance(message, dict):
                raise ValueError("message must be an object")
            result = driver.process(message)
        except (ValueError, TypeError, KeyError, OverflowError) as exc:
            errors += 1
            result = {"event": "transport_error", "line": number, "error_type": type(exc).__name__}
        destination.write(json.dumps(result, allow_nan=False) + "\n")
        destination.flush()
    return 1 if errors else 0
