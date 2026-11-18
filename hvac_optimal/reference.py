"""Supplied optimal-start AND optimal-stop behavior, without added guards.

See docs/reference-contract.md for source provenance and SDK-stub boundaries.
Only the standard library is required. Temperatures use one consistent unit;
the supplied defaults are Fahrenheit and minutes per Fahrenheit degree.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass, field
from datetime import datetime, time, timedelta, timezone, tzinfo
import math
import struct
from typing import Callable


SOURCE_SHA256 = "0F2B759951F18DEC2BA05C09D8B03569C90C0D69B3BB08CC18FFB9009FE3A539"
NO_CALCULATION, START_CALCULATION, START_IN_PROCESS = 0, 1, 2
STOP_CALCULATION, STOP_IN_PROCESS = 3, 4
MINUTE_MS, DAY_MS = 60_000, 86_400_000
EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)
RATE_NAMES = (
    "runtime_per_degree_cooling", "runtime_per_degree_heating",
    "drifttime_per_degree_cooling", "drifttime_per_degree_heating",
)


def float32(value: float) -> float:
    """Java float narrowing, including overflow to signed infinity."""
    try:
        return struct.unpack("!f", struct.pack("!f", value))[0]
    except OverflowError:
        return math.copysign(math.inf, value)


def java_int(value: float) -> int:
    """Java floating-to-int narrowing: truncate, saturate, NaN -> zero."""
    if math.isnan(value):
        return 0
    if value >= 2_147_483_647:
        return 2_147_483_647
    if value <= -2_147_483_648:
        return -2_147_483_648
    return int(value)


def int32(value: int) -> int:
    return (value + 2**31) % 2**32 - 2**31


def ieee_divide(numerator: float, denominator: float) -> float:
    """IEEE division, rather than Python's exception on a zero divisor."""
    if denominator == 0.0:
        if numerator == 0.0 or math.isnan(numerator):
            return math.nan
        sign = math.copysign(1.0, numerator) * math.copysign(1.0, denominator)
        return math.copysign(math.inf, sign)
    return numerator / denominator


def _json_value(value):
    if isinstance(value, (datetime, time)):
        return value.isoformat()
    if isinstance(value, float) and not math.isfinite(value):
        return "NaN" if math.isnan(value) else ("Infinity" if value > 0 else "-Infinity")
    if isinstance(value, dict):
        return {key: _json_value(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_json_value(item) for item in value]
    return value


@dataclass
class TimeAdapter:
    """Declared Baja-time emulation; not a certification of SDK semantics."""

    station_timezone: tzinfo = timezone.utc

    def local(self, value: datetime | None) -> datetime:
        value = EPOCH if value is None else value
        if value.tzinfo is None:
            value = value.replace(tzinfo=self.station_timezone)
        return value.astimezone(self.station_timezone)

    def epoch_millis(self, value: datetime | None) -> int:
        delta = self.local(value).astimezone(timezone.utc) - EPOCH
        return (delta.days * 86_400 + delta.seconds) * 1000 + delta.microseconds // 1000

    def time_of_day_millis(self, value: datetime | None) -> int:
        value = self.local(value)
        return ((value.hour * 60 + value.minute) * 60 + value.second) * 1000 + value.microsecond // 1000

    def day_of_year(self, value: datetime | None) -> int:
        return self.local(value).timetuple().tm_yday

    def elapsed_minutes(self, beginning: datetime | None, end: datetime | None) -> int:
        millis = self.epoch_millis(end) - self.epoch_millis(beginning)
        minutes = abs(millis) // MINUTE_MS
        return int32(-minutes if millis < 0 else minutes)

    @staticmethod
    def clock_millis(value: time | str) -> int:
        value = time.fromisoformat(value) if isinstance(value, str) else value
        return ((value.hour * 60 + value.minute) * 60 + value.second) * 1000 + value.microsecond // 1000

    @staticmethod
    def clock_time(millis: int) -> time:
        millis %= DAY_MS
        hour, millis = divmod(millis, 3_600_000)
        minute, millis = divmod(millis, MINUTE_MS)
        second, millis = divmod(millis, 1000)
        return time(hour, minute, second, millis * 1000)

    def next_clock_ticket(self, after: datetime) -> datetime:
        local = self.local(after)
        return local.replace(second=0, microsecond=0) + timedelta(minutes=1, seconds=15)


@dataclass
class Config:
    upper_comfort_limit: float = 77.0
    lower_comfort_limit: float = 68.0
    dynamic_parameter_adjust: bool = True
    old_parameter_multiplier: int = 2
    earliest_start_time: time | str = time(0, 0, 10)
    earliest_stop_time: time | str = time(16)
    runtime_per_degree_cooling: float = 10.0
    runtime_per_degree_heating: float = 10.0
    drifttime_per_degree_cooling: float = 10.0
    drifttime_per_degree_heating: float = 10.0


@dataclass
class Inputs:
    space_temp: float = 0.0
    outside_temp: float = 0.0
    start_enable: bool = False
    stop_enable: bool = False
    schedule_status: bool = False
    next_event_time: datetime | None = None
    next_event_value: bool = False
    heat_cool_mode: bool = False
    space_temp_valid: bool = True
    # Retained for adapters/audit; Java checks none of these other statuses.
    input_statuses: dict = field(default_factory=dict)


@dataclass
class Command:
    value: bool = False
    status_null: bool = True
    status_flags: int = 0


@dataclass
class State:
    program_mode: int = NO_CALCULATION
    last_program_mode: int = NO_CALCULATION
    start_done: bool = False
    analysis_complete: bool = False
    control_mode_at_beginning: bool = False
    observed_minutes_per_degree: float = 0.0
    space_temp_change: float = 0.0
    lead_time: int = 0
    optimized_runtime_minutes: int = 0
    runtime_per_degree_cooling: float = 10.0
    runtime_per_degree_heating: float = 10.0
    drifttime_per_degree_cooling: float = 10.0
    drifttime_per_degree_heating: float = 10.0
    now: datetime | None = None
    last_start_time: datetime | None = None
    last_stop_time: datetime | None = None
    parameter_reset_time: datetime | None = None
    space_temp_at_beginning: float = 0.0
    outside_temp_at_beginning: float = 0.0
    calculated_command_time: time = time(0)
    start_time_command: Command = field(default_factory=Command)
    stop_time_command: Command = field(default_factory=Command)
    message: str = ""

    def to_dict(self) -> dict:
        return _json_value(asdict(self))


@dataclass(frozen=True)
class TickResult:
    state: State
    events: tuple[dict, ...]

    def to_dict(self) -> dict:
        return {"state": self.state.to_dict(), "events": _json_value(self.events)}


class OptimizedStartStop:
    """Frozen native formulas and eligibility; research selection stays outside."""

    def __init__(self, config: Config | None = None, *,
                 clock: Callable[[], datetime] | None = None,
                 time_adapter: TimeAdapter | None = None,
                 on_event: Callable[[dict], None] | None = None):
        self.config = deepcopy(config) if config is not None else Config()
        self.clock = clock if clock is not None else lambda: datetime.now(timezone.utc)
        self.time_adapter = time_adapter if time_adapter is not None else TimeAdapter()
        self.on_event = on_event
        self.state = State(**{name: float32(getattr(self.config, name)) for name in RATE_NAMES})
        self.user_parameters = {name + "_user_defined": 0.0 for name in RATE_NAMES}
        self._events: list[dict] = []

    def next_clock_ticket(self, after: datetime) -> datetime:
        return self.time_adapter.next_clock_ticket(after)

    def user_parameter_changed(self, name: str, value: float, *,
                               now: datetime | None = None,
                               running: bool = True, steady_state: bool = True) -> bool:
        """Mirror changed(user-defined-property), including the running gate."""
        aliases = {
            "runtimePerDegreeCoolingUserDefined": "runtime_per_degree_cooling_user_defined",
            "runtimePerDegreeHeatingUserDefined": "runtime_per_degree_heating_user_defined",
            "drifttimePerDegreeCoolingUserDefined": "drifttime_per_degree_cooling_user_defined",
            "drifttimePerDegreeHeatingUserDefined": "drifttime_per_degree_heating_user_defined",
        }
        name = aliases.get(name, name)
        if name not in self.user_parameters:
            return False
        self.user_parameters[name] = float32(value)
        if running and steady_state:
            setattr(self.state, name.removesuffix("_user_defined"), float32(value))
            self.state.parameter_reset_time = now if now is not None else self.clock()
            return True
        return False

    def tick(self, inputs: Inputs, *, now: datetime | None = None) -> TickResult:
        """One doCalculate action. Explicit now freezes all clock reads for replay."""
        self._events = []
        read_clock = self.clock if now is None else lambda: now
        state = self.state
        state.now = read_clock()
        if not inputs.start_enable or self.time_adapter.time_of_day_millis(state.now) < MINUTE_MS:
            state.start_done = False
        self._analyze(inputs)
        self._calculate(inputs)
        self._control(inputs, read_clock)
        self._output()
        state.last_program_mode = state.program_mode
        result = TickResult(deepcopy(state), tuple(deepcopy(self._events)))
        if self.on_event is not None:
            for event in result.events:
                self.on_event(_json_value(deepcopy(event)))
        return result

    def _calculate(self, inputs: Inputs) -> None:
        state, config = self.state, self.config
        upper, lower = float32(config.upper_comfort_limit), float32(config.lower_comfort_limit)
        if self.time_adapter.day_of_year(inputs.next_event_time) != self.time_adapter.day_of_year(state.now):
            state.program_mode = NO_CALCULATION
        elif inputs.next_event_value:
            if inputs.start_enable and not inputs.schedule_status:
                if not state.start_done and inputs.space_temp_valid:
                    if state.program_mode != START_IN_PROCESS:
                        state.program_mode = START_CALCULATION
                        state.lead_time = self._start_lead(inputs, upper, lower)
                else:
                    state.lead_time = 0
            else:
                state.program_mode = NO_CALCULATION
        else:
            if inputs.stop_enable and inputs.schedule_status:
                if inputs.space_temp_valid and state.program_mode != STOP_IN_PROCESS:
                    state.program_mode = STOP_CALCULATION
                    if inputs.space_temp > lower:
                        state.control_mode_at_beginning = inputs.heat_cool_mode
                        state.lead_time = self._stop_lead(inputs, upper, lower)
                else:
                    state.lead_time = 0
            else:
                state.program_mode = NO_CALCULATION

    def _start_lead(self, inputs: Inputs, upper: float, lower: float) -> int:
        if inputs.space_temp > upper:
            return int32(1 + java_int((inputs.space_temp - upper) * self.state.runtime_per_degree_cooling))
        if inputs.space_temp < lower:
            return int32(1 + java_int((lower - inputs.space_temp) * self.state.runtime_per_degree_heating))
        return 0

    def _stop_lead(self, inputs: Inputs, upper: float, lower: float) -> int:
        if not inputs.heat_cool_mode:
            return java_int((inputs.space_temp - lower) * self.state.drifttime_per_degree_heating)
        return java_int((upper - inputs.space_temp) * self.state.drifttime_per_degree_cooling)

    def _control(self, inputs: Inputs, read_clock: Callable[[], datetime]) -> None:
        state, config, adapter = self.state, self.config, self.time_adapter
        event_ms = adapter.time_of_day_millis(inputs.next_event_time)
        if state.program_mode not in (START_CALCULATION, STOP_CALCULATION):
            state.calculated_command_time = adapter.clock_time(event_ms)
            return
        calculated = event_ms - state.lead_time * MINUTE_MS
        earliest_start = adapter.clock_millis(config.earliest_start_time)
        if calculated < earliest_start:
            calculated = earliest_start
        state.calculated_command_time = adapter.clock_time(calculated)
        if state.program_mode == STOP_CALCULATION and adapter.clock_millis(state.calculated_command_time) < adapter.clock_millis(config.earliest_stop_time):
            state.calculated_command_time = adapter.clock_time(adapter.clock_millis(config.earliest_stop_time))
        current_ms = adapter.time_of_day_millis(read_clock())
        if current_ms > adapter.clock_millis(state.calculated_command_time) or current_ms > event_ms:
            starting = state.program_mode == START_CALCULATION
            if starting:
                state.start_done = True
                state.program_mode = START_IN_PROCESS
                state.last_start_time = read_clock()
                actual_time = state.last_start_time
            else:
                state.program_mode = STOP_IN_PROCESS
                state.last_stop_time = read_clock()
                actual_time = state.last_stop_time
                state.control_mode_at_beginning = inputs.heat_cool_mode
            state.space_temp_at_beginning = inputs.space_temp
            state.outside_temp_at_beginning = inputs.outside_temp
            kind = "start" if starting else "stop"
            self._events.append({"type": "trigger", "kind": kind, "time": actual_time,
                                 "next_event_time": inputs.next_event_time,
                                 "space_temp": inputs.space_temp, "outside_temp": inputs.outside_temp})
            state.message = (f"Optimized {kind} for {inputs.next_event_time} schedule time.  "
                             f"Space temp is {inputs.space_temp:.1f}.")

    def _output(self) -> None:
        state = self.state
        state.start_time_command.value = state.program_mode == START_IN_PROCESS
        state.start_time_command.status_null = state.program_mode != START_IN_PROCESS
        state.stop_time_command.value = False
        state.stop_time_command.status_null = state.program_mode != STOP_IN_PROCESS
        if state.program_mode not in (START_IN_PROCESS, STOP_IN_PROCESS):
            state.analysis_complete = False

    def _analyze(self, inputs: Inputs) -> None:
        state, config = self.state, self.config
        if not (config.dynamic_parameter_adjust and not state.analysis_complete and inputs.space_temp_valid):
            return
        upper, lower = float32(config.upper_comfort_limit), float32(config.lower_comfort_limit)
        beginning, current = state.space_temp_at_beginning, inputs.space_temp
        name = None
        starting = state.last_program_mode == START_IN_PROCESS
        if starting:
            cooling = beginning > upper
            if cooling:
                if current < beginning and (current <= upper or inputs.schedule_status):
                    name = "runtime_per_degree_cooling"
                    change = float32(beginning - current)
            elif current > beginning and (current >= lower or inputs.schedule_status):
                name = "runtime_per_degree_heating"
                change = float32(current - beginning)
        elif state.last_program_mode == STOP_IN_PROCESS:
            if not state.control_mode_at_beginning:
                if current < beginning and (current <= lower or not inputs.schedule_status):
                    name = "drifttime_per_degree_heating"
                    change = float32(float32(beginning) - float32(current))
            elif current > beginning and (current >= upper or not inputs.schedule_status):
                name = "drifttime_per_degree_cooling"
                change = float32(float32(current) - float32(beginning))
        if name is None:
            return
        start_time = state.last_start_time if starting else state.last_stop_time
        elapsed = self.time_adapter.elapsed_minutes(start_time, state.now)
        state.space_temp_change = change
        state.optimized_runtime_minutes = elapsed
        observed = float32(ieee_divide(float32(elapsed), change))
        state.observed_minutes_per_degree = observed
        old = getattr(state, name)
        multiplier = int32(config.old_parameter_multiplier)
        weighted = float32(old * float32(multiplier))
        numerator = float32(weighted + observed)
        updated = float32(ieee_divide(numerator, float32(int32(multiplier + 1))))
        setattr(state, name, updated)
        state.analysis_complete = True
        kind = "start" if starting else "stop"
        target_reached = (current <= upper if name == "runtime_per_degree_cooling" else
                          current >= lower if name == "runtime_per_degree_heating" else
                          current <= lower if name == "drifttime_per_degree_heating" else current >= upper)
        self._events.append({"type": "native_learning", "kind": kind,
                             "parameter": name, "time": state.now,
                             "beginning_time": start_time,
                             "beginning_space_temp": beginning, "space_temp": current,
                             "temperature_change": change, "elapsed_minutes": elapsed,
                             "observed_minutes_per_degree": observed,
                             "old_minutes_per_degree": old, "new_minutes_per_degree": updated,
                             "target_reached": target_reached,
                             "schedule_status": inputs.schedule_status})
        state.message = (f"Optimized {kind} analysis done at {state.now}.  "
                         f"Space temp is {inputs.space_temp:.1f}.")


class ResearchOptimizedStartStop(OptimizedStartStop):
    """Explicit research extension: replace lead at native prediction branches.

    Callback: ``lead_predictor(kind, inputs, state_snapshot, default_lead)``.
    Native eligibility, analysis and subsequent command-time clamps still run.
    Supplying a callback intentionally changes native prediction behavior.
    """

    def __init__(self, *args, lead_predictor: Callable[[str, Inputs, State, int], int], **kwargs):
        super().__init__(*args, **kwargs)
        self.lead_predictor = lead_predictor

    def _start_lead(self, inputs: Inputs, upper: float, lower: float) -> int:
        native = super()._start_lead(inputs, upper, lower)
        return int32(self.lead_predictor("start", deepcopy(inputs), deepcopy(self.state), native))

    def _stop_lead(self, inputs: Inputs, upper: float, lower: float) -> int:
        native = super()._stop_lead(inputs, upper, lower)
        return int32(self.lead_predictor("stop", deepcopy(inputs), deepcopy(self.state), native))
