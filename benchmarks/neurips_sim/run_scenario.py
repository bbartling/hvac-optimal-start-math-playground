"""Closed-loop optimal start/stop benchmark on the NeurIPS 2026 Smart Buildings simulator.

One run = one scenario (building x weather strip, 30 days, 5-minute steps) with
ONE start algorithm and ONE stop algorithm applied to every AHU. The plant is
controlled by the G36 sequence from the neurips repo (``sac_trim/g36_backbone.py``,
the v6/v7 lineage); only the start decision and the early-stop decision are
swapped. Algorithms from ``hvac_optimal`` are wired in through two small hooks
that are patched into an in-memory copy of the backbone (the neurips repo is
never modified).

Special arms:
  start=v6      native v6 start (V7_COMPATIBILITY_MODE=True, learned AHU rate)
  start=v7      native v7 policy (RecoveryLearner, occupancy trees), native stop
  start=sac_trim  neurips SAC trim policy (best_actor.json), native v7 stop
  stop=v6       native backbone stop (recovery-rate proxy)

Usage (Windows, from the neurips repo venv):
  $env:SMART_BUILDINGS_KIT = "<neurips repo>\\.kit"
  python run_scenario.py --neurips-root <neurips repo> --scenario-dir <...\\training_scenarios\\building_train_1\\fairbanks_1> \
      --start robust_rls --stop first_order_coast --out results\\run.json
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
import types
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))

from hvac_optimal import (  # noqa: E402
    CoastSample, OptimalStartPlanner, OptimalStopPlanner, RecoveryEvent, ZoneReading,
)

K0 = 273.15


def k2f(k):
    return (k - K0) * 1.8 + 32.0


def dk2f(dk):
    return dk * 1.8


# ----------------------------------------------------------------------------- backbone
START_LINE = ('                    lead = min(START_MAX_LEAD_H, raw_lead_h * START_SAFETY + START_BUFFER_H)'
              ' if raw_lead_h > 0 else 0.0\n')
STOP_CALL = '            self._optimal_stop_decision(ahu, tz, hour, weekday, sched_occ, occupied)\n'


def load_backbone(neurips_root: Path, compat: bool):
    src = (neurips_root / "sac_trim" / "g36_backbone.py").read_text(encoding="utf-8")
    assert src.count(START_LINE) == 1, "start hook anchor not found"
    assert src.count(STOP_CALL) == 1, "stop hook anchor not found"
    src = src.replace(START_LINE, START_LINE +
                      '                    if getattr(self, "start_hook", None) is not None:\n'
                      '                        lead = self.start_hook(ahu, tz_ok, oat, hour, weekday, hours_to_start, lead)\n')
    src = src.replace(STOP_CALL,
                      '            (getattr(self, "stop_hook", None) or self._optimal_stop_decision)'
                      '(ahu, tz, hour, weekday, sched_occ, occupied)\n')
    mod = types.ModuleType("g36_backbone_hooked")
    mod.__file__ = str(neurips_root / "sac_trim" / "g36_backbone.py")
    sys.modules[mod.__name__] = mod  # dataclasses need the module registered
    exec(compile(src, mod.__file__, "exec"), mod.__dict__)
    mod.V7_COMPATIBILITY_MODE = bool(compat)
    return mod


# ----------------------------------------------------------------------------- hooked policy
class Bookkeeper:
    """Per-AHU learning bookkeeping for hvac_optimal planners (no future data)."""

    def __init__(self, policy, start_name, stop_name, holidays, max_lead, track_minutes=240):
        self.p = policy
        self.start_name, self.stop_name = start_name, stop_name
        # robust_rls runs on the AHU critical-zone group; "<model>_group" / "<model>_zone" override
        fb = start_name.endswith("_fb")
        if fb:
            start_name = start_name[:-3]
        if start_name.endswith("_group"):
            base, group = start_name[:-6], True
        elif start_name.endswith("_zone"):
            base, group = start_name[:-5], False
        else:
            base, group = start_name, start_name.startswith("robust_rls")
        self.group = group
        self.max_lead = max_lead
        self.planners = {}
        self.stoppers = {}
        for ahu in policy.ahus:
            if base.startswith("fixed_"):
                self.planners[ahu["id"]] = None
            elif start_name in ("v6", "v7", "sac_trim"):
                self.planners[ahu["id"]] = None
            else:
                self.planners[ahu["id"]] = OptimalStartPlanner(base, max_lead=max_lead, min_lead=10.0, group=group,
                                                               arrival_feedback=fb)
            if stop_name not in ("v6", "native"):
                self.stoppers[ahu["id"]] = OptimalStopPlanner(stop_name, max_early=120.0, guard=0.9, restart_guard=0.27)
        self.fixed = float(base.split("_")[1]) if base.startswith("fixed_") else None
        self.holidays = holidays
        self.track = {}           # ahu_id -> dict while a recovery is being tracked
        self.prev = {}            # ahu_id -> (running, temps_F, oat_F, sched_occ)
        self.track_minutes = track_minutes
        self.post_weekend_today = False
        self.cur_date = None
        self.prev_day_occupied = True
        self.events_learned = 0
        self.lead_log = []        # diagnostics: start commits and learned events
        self.last_lead = {}
        self.prev_warm = {}

    # -- helpers
    def zones_f(self, ahu, tz_k):
        return [ZoneReading(z["vav"], k2f(t), k2f(self.p.occ_heat), k2f(self.p.occ_cool))
                for z, t in zip(ahu["zones"], tz_k)]

    # -- start hook (called by the backbone while waiting to start)
    def start_hook(self, ahu, tz_ok, oat, hour, weekday, hours_to_start, native_lead_h):
        if self.fixed is not None:
            return self.fixed / 60.0
        planner = self.planners[ahu["id"]]
        zones = self.zones_f(ahu, tz_ok)
        lead_min = planner.lead_minutes(zones, k2f(oat), self.post_weekend_today)
        crit = planner.critical(planner._eligible(zones))
        self.last_lead[ahu["id"]] = (round(lead_min, 1), round(hours_to_start * 60.0, 1),
                                     round(crit.deficit(), 2) if crit is not None else 0.0)
        return lead_min / 60.0

    # -- stop hook (replaces backbone _optimal_stop_decision)
    def stop_hook(self, ahu, zone_t, hour, weekday, sched_occ, occupied):
        p = self.p
        st = self.stoppers[ahu["id"]]
        if not sched_occ:
            ahu["optimal_stop"] = False
            ahu["stop_blocked"] = False
            return
        if not (occupied and weekday < 5 and p.morning_start <= hour < p.occupied_end_hour):
            ahu["optimal_stop"] = False
            return
        if not np.all(np.isfinite(zone_t)) or len(zone_t) == 0:
            if ahu["optimal_stop"]:
                ahu["optimal_stop"] = False
                ahu["stop_blocked"] = True
            return
        zones = self.zones_f(ahu, zone_t)
        if ahu["optimal_stop"]:
            if st.should_restart(zones):
                ahu["optimal_stop"] = False
                ahu["stop_blocked"] = True
            return
        if ahu["stop_blocked"]:
            return
        minutes_to_end = (p.occupied_end_hour - hour) * 60.0
        if st.should_stop(minutes_to_end, zones, k2f(self.oat_k), occupied=True):
            ahu["optimal_stop"] = True

    # -- called after every get_action with the current scan's state
    def after_scan(self, step, ts, tz_by_ahu, oat_k, sched_occ, weekday):
        oat_f = k2f(oat_k)
        date = ts.date()
        if date != self.cur_date:
            # new calendar day: was yesterday a weekend/holiday?
            yday = date - __import__("datetime").timedelta(days=1)
            self.post_weekend_today = (yday.weekday() >= 5) or (yday in self.holidays)
            self.cur_date = date
        minute = step * 5.0
        for ahu in self.p.ahus:
            aid = ahu["id"]
            tz = tz_by_ahu[aid]
            if tz is None:
                continue
            temps_f = [k2f(t) for t in tz]
            running = bool(ahu["running"])
            w = bool(ahu.get("warmup", False))
            if w and not self.prev_warm.get(aid, False) and aid in self.last_lead:
                self.lead_log.append(dict(kind="commit", date=str(date), ahu=aid, minute=minute,
                                          lead=self.last_lead[aid][0], to_occ=self.last_lead[aid][1],
                                          deficit_f=self.last_lead[aid][2], pw=self.post_weekend_today))
            self.prev_warm[aid] = w
            # ---- coast learning (AHU off for the whole last interval)
            if aid in self.stoppers and aid in self.prev:
                prun, ptemps, poat, pocc = self.prev[aid]
                if not prun and not running:
                    for z, t0, t1 in zip(ahu["zones"], ptemps, temps_f):
                        if math.isfinite(t0) and math.isfinite(t1):
                            self.stoppers[aid].learn(z["vav"], CoastSample(t0, t1, poat, 5.0, bool(pocc)))
            self.prev[aid] = (running, temps_f, oat_f, sched_occ)
            # ---- recovery tracking for start learning
            planner = self.planners.get(aid)
            if planner is None:
                continue
            tr = self.track.get(aid)
            starting = (ahu["warmup"] or sched_occ) and running and tr is None and not self._done_today(aid, date)
            if starting and (sched_occ or ahu["warmup"]):
                self.track[aid] = tr = {"date": date, "t0": minute, "temps0": temps_f, "oat0": oat_f,
                                        "traj": [], "oats": [], "occ_min": None, "occ_temps": None,
                                        "pw": self.post_weekend_today}
                self._mark_done(aid, date)
            if tr is None:
                continue
            tr["traj"].append((minute - tr["t0"], temps_f))
            tr["oats"].append(oat_f)
            if sched_occ and tr["occ_min"] is None:
                tr["occ_min"] = minute
                tr["occ_temps"] = temps_f
            if minute - tr["t0"] >= self.track_minutes + 120 or (tr["occ_min"] is not None and minute - tr["occ_min"] >= 120):
                self._learn(ahu, planner, tr)
                self.track[aid] = None

    def _done_today(self, aid, date):
        return getattr(self, "_done", {}).get(aid) == date

    def _mark_done(self, aid, date):
        if not hasattr(self, "_done"):
            self._done = {}
        self._done[aid] = date

    def _learn(self, ahu, planner, tr):
        hsp, csp = k2f(self.p.occ_heat), k2f(self.p.occ_cool)
        traj = tr["traj"]
        oat_mean = float(np.mean(tr["oats"])) if tr["oats"] else tr["oat0"]
        nz = len(ahu["zones"])

        def zone_event(series, mode, target, start_temp, occ_temp):
            reach = None
            for t, temp in series:
                if (mode == "heat" and temp >= target) or (mode == "cool" and temp <= target):
                    reach = t
                    break
            arr = None
            if occ_temp is not None:
                arr = (target - occ_temp) if mode == "heat" else (occ_temp - target)
            # trajectory for Model 4: start .. occupancy + 60 min (PNNL training window)
            lim = (tr["occ_min"] - tr["t0"] + 60) if tr["occ_min"] is not None else 1e9
            return RecoveryEvent(mode=mode, start_temp=start_temp, target=target, oat=tr["oat0"],
                                 minutes_to_target=reach, trajectory=[(t, v) for t, v in series if t <= lim],
                                 post_weekend=tr["pw"], oat_mean=oat_mean, arrival_error=arr)

        if planner.group:
            # per-zone outcomes first (reached the band by the end of tracking?)
            bad_before = planner.nonrecovering()
            for i, z in enumerate(ahu["zones"]):
                t0z = tr["temps0"][i]
                if hsp <= t0z <= csp:
                    continue
                reached = any((hsp <= temps[i] <= csp) for _, temps in traj)
                planner.record_outcome(z["vav"], reached)
            # critical-zone group over zones that are NOT capacity-limited
            keep = [i for i, z in enumerate(ahu["zones"]) if z["vav"] not in bad_before] or list(range(nz))
            t0 = [tr["temps0"][i] for i in keep]
            traj = [(t, [temps[i] for i in keep]) for t, temps in traj]
            if tr["occ_temps"] is not None:
                tr = dict(tr, occ_temps=[tr["occ_temps"][i] for i in keep])
            if tr["occ_temps"] is not None:
                # arrival feedback: worst kept-zone deficit at occupancy start (deg F)
                planner.record_arrival(max(max(hsp - x, x - csp, 0.0) for x in tr["occ_temps"]))
            dh = max(hsp - x for x in t0)
            dc = max(x - csp for x in t0)
            if max(dh, dc) <= 0:
                return
            mode = "heat" if dh >= dc else "cool"
            if mode == "heat":
                series = [(t, hsp - max(hsp - x for x in temps)) for t, temps in traj]
                target = hsp
            else:
                series = [(t, csp + max(x - csp for x in temps)) for t, temps in traj]
                target = csp
            occ_temp = None
            if tr["occ_temps"] is not None:
                ot = tr["occ_temps"]
                occ_temp = (hsp - max(hsp - x for x in ot)) if mode == "heat" else (csp + max(x - csp for x in ot))
            ev = zone_event(series, mode, target, series[0][1], occ_temp)
            self.lead_log.append(dict(kind="event", date=str(tr["date"]), ahu=ahu["id"], mode=mode,
                                      delta_f=round(ev.delta, 2), t_reach=ev.minutes_to_target,
                                      occ_after=(tr["occ_min"] - tr["t0"]) if tr["occ_min"] is not None else None,
                                      n_excluded=nz - len(keep), oat_f=round(tr["oat0"], 1)))
            planner.learn("__group__", ev)
            self.events_learned += 1
            return
        for i, z in enumerate(ahu["zones"]):
            t0 = tr["temps0"][i]
            if t0 < hsp:
                mode, target = "heat", hsp
            elif t0 > csp:
                mode, target = "cool", csp
            else:
                continue
            series = [(t, temps[i]) for t, temps in traj]
            occ_temp = tr["occ_temps"][i] if tr["occ_temps"] is not None else None
            planner.learn(z["vav"], zone_event(series, mode, target, t0, occ_temp))
            self.events_learned += 1


# ----------------------------------------------------------------------------- run
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--neurips-root", required=True)
    ap.add_argument("--scenario-dir", required=True)
    ap.add_argument("--start", required=True)
    ap.add_argument("--stop", default="v6")
    ap.add_argument("--steps", type=int, default=8640)
    ap.add_argument("--max-lead", type=float, default=180.0)
    ap.add_argument("--actor", default=None, help="SAC trim actor json (start=sac_trim)")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    root = Path(a.neurips_root).resolve()
    scen = Path(a.scenario_dir).resolve()
    out = Path(a.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("SMART_BUILDINGS_KIT", str(root / ".kit"))
    os.environ.setdefault("NUMBA_CACHE_DIR", str(root / ".nbcache"))
    sys.path.insert(0, str(root))
    from sac_trim import sim  # chdirs into the kit

    env = sim.ev.load_hybrid_environment(scen / "config.gin")
    meta = sim.ev.create_building_meta_data(env, scen)
    obs, _ = env.reset()

    if a.start == "sac_trim":
        from sac_trim.policy import NumpyActor, SacTrimPolicy
        policy = SacTrimPolicy(meta, env.action_spec(), actor=NumpyActor(json.loads(Path(a.actor).read_text())))
        stop_name = "native"
        bk = None
    elif a.start == "v7":
        bb = load_backbone(root, compat=False)
        policy = bb.G36HighSatPolicy(meta, env.action_spec())
        stop_name = "native"
        bk = None
    else:
        bb = load_backbone(root, compat=True)
        policy = bb.G36HighSatPolicy(meta, env.action_spec())
        stop_name = a.stop
        holidays = set()
        for h in (meta.get("holidays") or []):
            try:
                holidays.add(h.date() if hasattr(h, "date") else h)
            except Exception:
                pass
        bk = Bookkeeper(policy, a.start, stop_name, holidays, a.max_lead)
        if a.start != "v6":
            policy.start_hook = bk.start_hook
        if stop_name != "v6":
            policy.stop_hook = bk.stop_hook

    # observation indexes we log
    idx = policy.idx
    i_occ = policy.i_occ_now
    zone_idx = {ahu["id"]: [z["i_temp"] for z in ahu["zones"]] for ahu in policy.ahus}
    ahu_ids = [ahu["id"] for ahu in policy.ahus]

    T = a.steps
    nz_total = sum(len(v) for v in zone_idx.values())
    log_ts = []
    log_run = np.zeros((T, len(ahu_ids)), dtype=np.int8)
    log_warm = np.zeros((T, len(ahu_ids)), dtype=np.int8)  # 1 = start committed (warm-up mode)
    log_tz = np.full((T, nz_total), np.nan, dtype=np.float32)
    log_oat = np.zeros(T, dtype=np.float32)
    log_sched = np.zeros(T, dtype=np.int8)
    log_elec = np.zeros(T, dtype=np.float64)
    log_gas = np.zeros(T, dtype=np.float64)
    log_carbon = np.zeros(T, dtype=np.float64)
    log_occ = np.zeros(T, dtype=np.float32)
    log_reward = np.zeros(T, dtype=np.float64)
    log_prod = np.zeros(T, dtype=np.float64)
    zone_cols = []
    for aid in ahu_ids:
        for z in next(x for x in policy.ahus if x["id"] == aid)["zones"]:
            zone_cols.append((aid, z["vav"]))

    t0 = time.time()
    steps = 0
    for s in range(T):
        raw = np.asarray(obs, dtype=np.float64)
        pts = raw * policy.scale + policy.offset
        if bk is not None:
            bk.oat_k = pts[policy.i_oat] if np.isfinite(pts[policy.i_oat]) else 273.15
        act = policy.get_action(obs)
        ts = env.building.current_timestamp
        sched = raw[i_occ] > 0.5
        hour = policy._angle(raw[policy.i_hod[0]], raw[policy.i_hod[1]]) * 24 / (2 * np.pi)
        weekday = int(policy._angle(raw[policy.i_dow[0]], raw[policy.i_dow[1]]) * 7 / (2 * np.pi) + 1e-6) % 7
        if bk is not None:
            tz_by = {aid: pts[zone_idx[aid]] for aid in ahu_ids}
            bk.after_scan(s, ts, tz_by, bk.oat_k, sched, weekday)
        # log state at the decision instant
        log_ts.append(str(ts))
        log_tz[s] = pts[[i for aid in ahu_ids for i in zone_idx[aid]]]
        log_oat[s] = pts[policy.i_oat]
        log_sched[s] = 1 if sched else 0
        disc = act["discrete_action"]
        for k, ahu in enumerate(policy.ahus):
            log_run[s, k] = int(disc[ahu["d_run"]])
            log_warm[s, k] = int(bool(ahu.get("warmup", False)))
        obs, reward, term, trunc, _ = env.step(act)
        _, rr = env.get_reward_info_and_response()
        log_elec[s] = rr.electricity_energy_cost
        log_gas[s] = rr.natural_gas_energy_cost
        log_carbon[s] = rr.carbon_emitted
        log_occ[s] = rr.total_occupancy
        log_reward[s] = float(reward)
        log_prod[s] = rr.normalized_productivity_regret
        steps += 1
        if term or trunc:
            break

    n = steps
    np.savez_compressed(
        out.with_suffix(".npz"), ts=np.array(log_ts[:n]), run=log_run[:n], warm=log_warm[:n], tz=log_tz[:n], oat=log_oat[:n],
        sched=log_sched[:n], elec=log_elec[:n], gas=log_gas[:n], carbon=log_carbon[:n], occ=log_occ[:n],
        reward=log_reward[:n], prod=log_prod[:n],
        zone_ahu=np.array([c[0] for c in zone_cols]), zone_id=np.array([c[1] for c in zone_cols]),
        ahu_ids=np.array(ahu_ids))
    summary = {
        "building": scen.parent.name, "weather": scen.name, "start": a.start, "stop": stop_name,
        "steps": n, "score": float(-np.mean(log_reward[:n])), "minutes": round((time.time() - t0) / 60, 2),
        "occ_heat_k": float(policy.occ_heat), "occ_cool_k": float(policy.occ_cool),
        "morning_start": float(policy.morning_start), "occupied_end_hour": float(policy.occupied_end_hour),
        "holidays": sorted(str(h) for h in (meta.get("holidays") or [])),
        "n_ahu": len(ahu_ids), "n_zones": nz_total,
        "events_learned": bk.events_learned if bk else None,
        "diag": bk.lead_log if bk else None,
        "energy_cost_total": float(log_elec[:n].sum() + log_gas[:n].sum()),
    }
    out.write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
