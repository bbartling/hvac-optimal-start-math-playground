"""Multi-zone optimal-start planner.

Keeps one start model per zone (or per critical-zone group), predicts the
lead time for every zone that is outside its occupied band, and lets the
WORST zone decide (the air handler / RTU must start early enough for its
slowest zone). Call :meth:`should_start` every scan (e.g. every 5 or 15
minutes) during the pre-occupancy window, exactly like PNNL's agent
re-evaluates every 15 minutes until it commits.
"""
from __future__ import annotations

from typing import Callable, Dict, Iterable, Optional, Sequence, Union

from ._stats import clamp
from .start_models import StartModel, make_start_model
from .types import RecoveryEvent, ZoneReading

#: benchmark winner (see README "Results"): robust RLS, one model per AHU
#: critical-zone group, 10-180 min clamp
RECOMMENDED_START_MODEL = "robust_rls"


class OptimalStartPlanner:
    def __init__(self, model: Union[str, Callable[[], StartModel]] = RECOMMENDED_START_MODEL,
                 max_lead: float = 180.0, min_lead: float = 10.0, group: bool = False,
                 exclude_nonrecovering: bool = True, outcome_window: int = 3, fail_limit: int = 2,
                 arrival_feedback: bool = False, fb_tol: float = 0.5, fb_q: float = 0.8,
                 fb_step: float = 10.0, fb_max: float = 120.0):
        """
        model    : name in ``START_MODELS`` or a zero-arg factory
        max_lead : earliest allowed start (minutes before occupancy); also the
                   fallback while a model has no history (PNNL default 180)
        min_lead : latest allowed start (PNNL default 10)
        group    : if True, treat all zones as ONE critical-zone group whose
                   temperature is the worst zone (one model per planner)
        exclude_nonrecovering : ignore zones that failed to reach their
                   setpoint in ``fail_limit`` of their last ``outcome_window``
                   recoveries. No start time can fix a capacity-limited zone;
                   letting it vote only pins the start at ``max_lead`` and wastes
                   energy. Flagged zones are reported by :meth:`nonrecovering`.
        arrival_feedback : learn an extra lead (minutes, ``offset``) from what actually
                   happened after occupancy started (see :meth:`record_arrival`). It is
                   added to the model's lead, and it is also used as the lead on days when
                   every zone is in band at decision time. Zones that night cycling just
                   pulled into the band, or that lose ground to solar and internal gains
                   after the start, still get a start that way. The offset follows a
                   Robbins-Monro quantile update (step ``fb_step``, cap ``fb_max``), so the
                   share of days with a comfort deficit above ``fb_tol`` degrees converges
                   to ``1 - fb_q``.
        """
        self._factory = (lambda: make_start_model(model)) if isinstance(model, str) else model
        self.max_lead, self.min_lead, self.group = float(max_lead), float(min_lead), bool(group)
        self.models: Dict[str, StartModel] = {}
        self.exclude_nonrecovering = bool(exclude_nonrecovering)
        self.outcome_window, self.fail_limit = int(outcome_window), int(fail_limit)
        self.outcomes: Dict[str, list] = {}
        self.arrival_feedback = bool(arrival_feedback)
        self.fb_tol, self.fb_q, self.fb_step, self.fb_max = float(fb_tol), float(fb_q), float(fb_step), float(fb_max)
        self.offset = 0.0

    def record_outcome(self, zone_id: str, reached: bool) -> None:
        """Remember whether a zone reached its setpoint after a recovery."""
        h = self.outcomes.setdefault(zone_id, [])
        h.append(bool(reached))
        del h[:-self.outcome_window]

    def nonrecovering(self) -> set:
        return {z for z, h in self.outcomes.items() if sum(1 for r in h if not r) >= self.fail_limit}

    def _eligible(self, zones: Sequence[ZoneReading]) -> Sequence[ZoneReading]:
        if not self.exclude_nonrecovering:
            return zones
        bad = self.nonrecovering()
        keep = [z for z in zones if z.zone_id not in bad]
        return keep if keep else zones

    @classmethod
    def recommended(cls) -> "OptimalStartPlanner":
        return cls(RECOMMENDED_START_MODEL, max_lead=180.0, min_lead=10.0, group=True)

    def model_for(self, zone_id: str) -> StartModel:
        key = "__group__" if self.group else zone_id
        if key not in self.models:
            self.models[key] = self._factory()
        return self.models[key]

    @staticmethod
    def critical(zones: Sequence[ZoneReading]) -> Optional[ZoneReading]:
        """Zone with the largest deficit from its occupied band (None if all inside)."""
        worst = max(zones, key=lambda z: z.deficit(), default=None)
        return worst if worst is not None and worst.deficit() > 0 else None

    def zone_leads(self, zones: Sequence[ZoneReading], oat: float,
                   post_weekend: bool = False) -> Dict[str, float]:
        out: Dict[str, float] = {}
        candidates: Iterable[ZoneReading]
        zones = self._eligible(zones)
        if self.group:
            c = self.critical(zones)
            candidates = [c] if c is not None else []
        else:
            candidates = zones
        for z in candidates:
            mode = z.mode()
            if mode is None:
                out[z.zone_id] = 0.0
                continue
            p = self.model_for(z.zone_id).predict(mode, z.temp, z.target(), oat, post_weekend)
            out[z.zone_id] = self.max_lead if p is None else p
        return out

    def lead_minutes(self, zones: Sequence[ZoneReading], oat: float, post_weekend: bool = False) -> float:
        """Required lead (minutes), max over zones, clamped to [min_lead, max_lead].

        Returns 0 when every zone is already inside its occupied band.
        """
        return self._lead_now(zones, oat, post_weekend)

    def record_arrival(self, arrival_error: float) -> None:
        """Feed the comfort outcome of one morning (degrees outside the band).

        Use the worst (non-capacity-limited) zone's deficit at occupancy start, or a
        high percentile of it over the first occupied hour. > 0 means short.
        """
        if not self.arrival_feedback or arrival_error is None:
            return
        late = 1.0 if arrival_error > self.fb_tol else 0.0
        self.offset = clamp(self.offset + self.fb_step * (late - (1.0 - self.fb_q)), 0.0, self.fb_max)

    def _lead_now(self, zones, oat, post_weekend):
        leads = self.zone_leads(zones, oat, post_weekend)
        worst = max(leads.values(), default=0.0) + self.offset
        if worst <= 0:
            return 0.0
        return clamp(worst, self.min_lead, self.max_lead)

    def should_start(self, minutes_to_occupancy: float, zones: Sequence[ZoneReading], oat: float,
                     post_weekend: bool = False) -> bool:
        """True once the predicted lead is >= the time left before occupancy."""
        lead = self.lead_minutes(zones, oat, post_weekend)
        return lead > 0 and minutes_to_occupancy <= lead

    def learn(self, zone_id: str, event: RecoveryEvent) -> None:
        """Feed one finished recovery (for ``group=True`` pass the group event)."""
        if not self.group:
            self.record_outcome(zone_id, event.minutes_to_target is not None)
        self.model_for(zone_id).update(event)
