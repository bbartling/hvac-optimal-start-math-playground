"""Plain data types shared by the start and stop algorithms."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Optional, Sequence, Tuple

Mode = Literal["heat", "cool"]


@dataclass(frozen=True)
class ZoneReading:
    """One zone right now: temperature and the OCCUPIED comfort band."""
    zone_id: str
    temp: float
    heat_sp: float
    cool_sp: float

    def mode(self, deadband: float = 0.0) -> Optional[Mode]:
        """'heat' if below the heating setpoint, 'cool' if above cooling, else None."""
        if self.temp < self.heat_sp - deadband:
            return "heat"
        if self.temp > self.cool_sp + deadband:
            return "cool"
        return None

    def deficit(self) -> float:
        """Distance (>= 0) from the comfort band."""
        if self.temp < self.heat_sp:
            return self.heat_sp - self.temp
        if self.temp > self.cool_sp:
            return self.temp - self.cool_sp
        return 0.0

    def target(self) -> float:
        m = self.mode()
        return self.heat_sp if m == "heat" else self.cool_sp


@dataclass
class RecoveryEvent:
    """What one zone did during one morning recovery (one training sample).

    ``trajectory`` holds (minutes since the equipment started, zone temp),
    starting at minute 0. ``minutes_to_target`` is the observed time from start
    until the zone first reached ``target`` (None if it never did inside the
    observation window; models that need it skip the sample).
    ``arrival_error`` is the zone deficit at the occupancy start (>= 0 means
    short of the setpoint by that much, < 0 means past it), used by the PNNL
    Model 3 day-to-day correction term.
    """
    mode: Mode
    start_temp: float
    target: float
    oat: float
    minutes_to_target: Optional[float]
    trajectory: Sequence[Tuple[float, float]] = field(default_factory=tuple)
    post_weekend: bool = False
    oat_mean: Optional[float] = None
    arrival_error: Optional[float] = None

    @property
    def delta(self) -> float:
        """Initial deficit (>= 0) in the direction of recovery."""
        d = self.target - self.start_temp if self.mode == "heat" else self.start_temp - self.target
        return max(0.0, d)

    def progress(self) -> list[tuple[float, float]]:
        """(minutes, degrees recovered so far) along the trajectory."""
        sign = 1.0 if self.mode == "heat" else -1.0
        return [(t, sign * (temp - self.start_temp)) for t, temp in self.trajectory]

    def minutes_for_first_degree(self, degree: float = 1.0) -> Optional[float]:
        """Minutes per degree over the first ``degree`` of recovery (PNNL alpha_1b)."""
        for t, gained in self.progress():
            if gained >= degree and t > 0:
                return t / gained
        return None


@dataclass(frozen=True)
class CoastSample:
    """One interval with the air handler OFF (for coast / drift learning)."""
    temp_start: float
    temp_end: float
    oat: float
    minutes: float
    occupied: bool = False
