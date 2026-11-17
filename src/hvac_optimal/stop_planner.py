"""Multi-zone optimal-stop planner with comfort-based restart."""
from __future__ import annotations

from typing import Callable, Dict, Sequence, Union

from .stop_models import StopModel, make_stop_model
from .types import CoastSample, ZoneReading

RECOMMENDED_STOP_MODEL = "first_order_coast"


class OptimalStopPlanner:
    def __init__(self, model: Union[str, Callable[[], StopModel]] = RECOMMENDED_STOP_MODEL,
                 max_early: float = 120.0, guard: float = 0.9, restart_guard: float = 0.27):
        """
        max_early     : never stop more than this many minutes before the end
        guard         : the projected temperature must stay this far INSIDE the
                        occupied band (deg; 0.9 F = 0.5 K, as in the v6 backbone)
        restart_guard : once stopped, restart if a zone gets this close to a band
                        edge (0.27 F = 0.15 K)
        """
        self._factory = (lambda: make_stop_model(model)) if isinstance(model, str) else model
        self.max_early, self.guard, self.restart_guard = float(max_early), float(guard), float(restart_guard)
        self.models: Dict[str, StopModel] = {}

    @classmethod
    def recommended(cls) -> "OptimalStopPlanner":
        return cls(RECOMMENDED_STOP_MODEL)

    def model_for(self, zone_id: str) -> StopModel:
        if zone_id not in self.models:
            self.models[zone_id] = self._factory()
        return self.models[zone_id]

    def should_stop(self, minutes_to_end: float, zones: Sequence[ZoneReading], oat: float,
                    occupied: bool = True) -> bool:
        if not zones or not (0 < minutes_to_end <= self.max_early):
            return False
        for z in zones:
            m = self.model_for(z.zone_id)
            if m.never_stops:
                return False
            b = m.bounds(z.temp, oat, minutes_to_end, occupied)
            if b is None:
                return False
            lo, hi = b
            if lo < z.heat_sp + self.guard or hi > z.cool_sp - self.guard:
                return False
        return True

    def should_restart(self, zones: Sequence[ZoneReading]) -> bool:
        return any(z.temp <= z.heat_sp + self.restart_guard or z.temp >= z.cool_sp - self.restart_guard
                   for z in zones)

    def learn(self, zone_id: str, sample: CoastSample) -> None:
        self.model_for(zone_id).update(sample)
