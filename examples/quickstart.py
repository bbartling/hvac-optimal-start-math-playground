"""Minimal optimal start + optimal stop loop (no dependencies).

Run:  python examples/quickstart.py      (from the repo root, after `pip install -e .`)
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from hvac_optimal import (CoastSample, OptimalStartPlanner, OptimalStopPlanner, RecoveryEvent,
                          ZoneReading)

HEAT_SP, COOL_SP = 70.0, 75.0
start = OptimalStartPlanner.recommended()
stop = OptimalStopPlanner.recommended()

# --- a toy zone: 1R1C, recovers toward 78 F with a 60 min time constant -----------
def recover(t0, minutes):
    return 78.0 + (t0 - 78.0) * math.exp(-minutes / 60.0)

for day in range(10):
    oat = 25.0 + 3 * (day % 4)
    t0 = 62.0 - (day % 3)
    zones = [ZoneReading("ahu1", t0, HEAT_SP, COOL_SP)]
    lead = start.lead_minutes(zones, oat, post_weekend=(day % 5 == 0))
    traj = [(m, recover(t0, m)) for m in range(0, 241, 5)]
    actual = next(m for m, T in traj if T >= HEAT_SP)
    print(f"day {day}: zone {t0:.1f} F, OAT {oat:.0f} F -> start {lead:5.1f} min early "
          f"(needed {actual} min)")
    start.learn("ahu1", RecoveryEvent("heat", t0, HEAT_SP, oat, actual, traj,
                                      post_weekend=(day % 5 == 0), oat_mean=oat))

# --- optimal stop: learn the coast from unoccupied OFF periods, then ask ----------
for _ in range(30):
    stop.learn("z1", CoastSample(72.0, 71.7, 30.0, 30.0, occupied=False))
zones = [ZoneReading("z1", 72.5, HEAT_SP, COOL_SP)]
for m in (90, 60, 30):
    print(f"{m} min before unoccupied: stop now? {stop.should_stop(m, zones, oat=30.0)}")
