"""Turn benchmark traces (*.npz + *.json from run_scenario.py) into metrics.

Outputs (in --out):
  ahu_days.csv    one row per run x occupied day x AHU (start + stop metrics)
  days.csv        one row per run x occupied day (building energy / reward windows)
  runs.csv        one row per run (official episode score, energy)
  summary.md      the tables used in the README

Definitions (temperatures in K = deg C differences; band = occupied [heat_sp, cool_sp]):
  lead            minutes the AHU had been in warm-up (start committed) at occupancy start
  night_run       the fan ran >90 % of the pre-start night anyway (cold-climate night
                  setback heating); the start decision then only changes setpoints
  capable zone    a zone that is inside the band at some point during that occupied day
                  (capacity-limited zones that never recover are excluded from arrival
                  timing; no start time can fix them; they still count in unmet K*min)
  late (1F tol)   as late, but a zone counts as arrived within 1 F (0.56 K) of the band
                  (PNNL's allowable deviation)
  arrival error   + minutes after occupancy until the LAST capable zone entered the band
                  (late), or - minutes the capable zones had already been in band before
                  occupancy, capped at the lead (early = wasted runtime)
  unmet w/ people same, over the first 3 h of occupancy, only while people are in the building
  unmet K*min     sum over zones of the band deficit over the first 2 h of occupancy,
                  per zone (K*min / zone)
  morning window  4 h before to 2 h after occupancy start: building electricity+gas $
                  and the simulator's own reward (productivity regret + energy + carbon)
  stop window     the last 3 h of the occupied period: early-stop minutes, restarts,
                  unmet K*min / zone, energy $ and reward
  post-weekend    first occupied day after a day with no occupied period
  season          heating if the day's mean OAT < 10 C, cooling if > 18 C, else shoulder
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

STEP_MIN = 5.0
PRE = 72        # 6 h of 5-min steps before occupancy considered for lead
MORNING_PRE, MORNING_POST = 48, 24
STOP_WIN = 36
WARMUP_DAYS = 7
TOL_K = 1.0 / 1.8   # PNNL "allowable deviation" 1 F, used for the tolerant arrival metric


def city_of(weather: str) -> str:
    return weather.split("_")[0]


def analyze_run(js: Path):
    meta = json.loads(js.read_text())
    npz = js.with_suffix(".npz")
    if not npz.exists():
        return [], [], meta
    d = np.load(npz, allow_pickle=False)
    ts = pd.to_datetime(d["ts"])
    sched = d["sched"].astype(bool)
    run = d["run"]
    # start decision = AHU committed to warm-up (or running) before occupancy. Older traces
    # have no "warm" array; then only fan run status is known.
    warm = d["warm"] if "warm" in d.files else None
    tz = d["tz"].astype(float)
    oat = d["oat"].astype(float) - 273.15
    energy = d["elec"] + d["gas"]
    reward = d["reward"]
    people = d["occ"].astype(float) > 0.5
    zone_ahu = d["zone_ahu"]
    ahu_ids = list(d["ahu_ids"])
    hsp, csp = meta["occ_heat_k"], meta["occ_cool_k"]
    T = len(ts)
    dates = ts.normalize()
    deficit = np.maximum(np.maximum(hsp - tz, tz - csp), 0.0)
    inband = deficit <= 0.0
    near = deficit <= TOL_K   # PNNL allowable deviation (1 F)
    ep_start = dates[0]
    occ_dates = sorted(set(dates[sched]))
    occ_set = set(occ_dates)
    rows, drows = [], []
    for dt in occ_dates:
        idx = np.where((dates == dt) & sched)[0]
        i_occ, i_end = int(idx[0]), int(idx[-1]) + 1
        day_no = int((dt - ep_start).days)
        prev = dt - pd.Timedelta(days=1)
        pw = prev not in occ_set and day_no > 0
        lo = max(0, i_occ - PRE)
        start_ok = i_occ - PRE >= 0
        day_oat = float(np.nanmean(oat[lo:i_end]))
        season = "heating" if day_oat < 10 else ("cooling" if day_oat > 18 else "shoulder")
        drow = dict(date=str(dt.date()), day_no=day_no, dow=int(dt.dayofweek), post_weekend=pw,
                    season=season, oat_mean=day_oat, start_ok=start_ok,
                    morning_energy=float(energy[max(0, i_occ - MORNING_PRE):i_occ + MORNING_POST].sum()),
                    morning_reward=float(reward[max(0, i_occ - MORNING_PRE):i_occ + MORNING_POST].sum()),
                    evening_energy=float(energy[max(0, i_end - STOP_WIN):i_end].sum()),
                    evening_reward=float(reward[max(0, i_end - STOP_WIN):i_end].sum()),
                    day_energy=float(energy[np.where(dates == dt)[0]].sum()),
                    day_reward=float(reward[np.where(dates == dt)[0]].sum()))
        drows.append(drow)
        for a, aid in enumerate(ahu_ids):
            cols = np.where(zone_ahu == aid)[0]
            if len(cols) == 0:
                continue
            r = run[:, a]
            # ---- start: lead = minutes of warm-up mode before occupancy (falls back to
            # continuous fan runtime for traces without the warm-up log)
            st = warm[:, a] if warm is not None else r
            lead = 0.0
            j = i_occ
            while j - 1 >= lo and st[j - 1] == 1:
                j -= 1
            lead = (i_occ - j) * STEP_MIN
            night_run = bool(r[lo:j].mean() > 0.9) if j > lo else bool(r[lo])
            runtime_pre = float(r[lo:i_occ].sum() * STEP_MIN)
            day_in = inband[i_occ:i_end][:, cols]
            capable = cols[day_in.any(axis=0)]
            late = 0.0
            early = 0.0
            if len(capable):
                late_z = []
                for c in capable:
                    if inband[i_occ, c]:
                        late_z.append(0.0)
                    else:
                        k = np.argmax(inband[i_occ:i_end, c])
                        late_z.append(k * STEP_MIN)
                late = float(max(late_z))
                if late == 0.0:
                    k = i_occ
                    while k - 1 >= lo and inband[k - 1, capable].all():
                        k -= 1
                    early = min(lead, (i_occ - k) * STEP_MIN)
            arrival = late if late > 0 else -early
            # tolerant arrival (within 1 F of the band, PNNL's allowable deviation)
            late_tol = 0.0
            cap_t = cols[near[i_occ:i_end][:, cols].any(axis=0)]
            for c in cap_t:
                if not near[i_occ, c]:
                    late_tol = max(late_tol, float(np.argmax(near[i_occ:i_end, c]) * STEP_MIN))
            w2 = slice(i_occ, min(T, i_occ + 24))
            unmet = float(deficit[w2][:, cols].sum() * STEP_MIN / len(cols))
            unmet_cap = float(deficit[w2][:, capable].sum() * STEP_MIN / len(capable)) if len(capable) else np.nan
            w3 = slice(i_occ, min(T, i_occ + 36))
            unmet_people = float((deficit[w3][:, cols] * people[w3][:, None]).sum() * STEP_MIN / len(cols))
            maxdef_cap = float(deficit[i_occ, capable].max()) if len(capable) else np.nan
            # ---- stop
            s0 = max(i_occ, i_end - STOP_WIN)
            stop_lead = 0.0
            other_off = False
            if r[i_end - 1] == 0:
                k = i_end - 1
                while k - 1 >= s0 and r[k - 1] == 0:
                    k -= 1
                stop_lead = (i_end - k) * STEP_MIN
                other_off = (k == s0) and (s0 - 1 >= 0 and r[s0 - 1] == 0)
            seg = r[s0:i_end]
            restarts = int(((seg[1:] == 1) & (seg[:-1] == 0)).sum())
            off_min = float((seg == 0).sum() * STEP_MIN)
            sw = slice(s0, i_end)
            stop_unmet = float(deficit[sw][:, cols].sum() * STEP_MIN / len(cols))
            stop_maxdef = float(deficit[sw][:, cols].max())
            rows.append(dict(date=str(dt.date()), day_no=day_no, dow=int(dt.dayofweek), post_weekend=pw,
                             season=season, ahu=aid, n_zones=len(cols), n_capable=len(capable),
                             start_ok=start_ok, has_warm=warm is not None, night_run=night_run, lead=lead, runtime_pre=runtime_pre, late=late, late_tol=late_tol, early=early,
                             arrival=arrival, unmet=unmet, unmet_cap=unmet_cap, unmet_people=unmet_people, maxdef_cap=maxdef_cap,
                             inband_frac=float(inband[i_occ, cols].mean()),
                             stop_lead=stop_lead, stop_other_off=bool(other_off), stop_off_min=off_min,
                             restarts=restarts, stop_unmet=stop_unmet, stop_maxdef=stop_maxdef))
    return rows, drows, meta


def q(x, p):
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    return float(np.percentile(x, p)) if len(x) else np.nan


def md_table(df: pd.DataFrame, floatfmt="{:.2f}") -> str:
    cols = list(df.columns)
    out = ["| " + " | ".join(str(c) for c in cols) + " |", "|" + "|".join("---" for _ in cols) + "|"]
    for _, r in df.iterrows():
        cells = []
        for c in cols:
            v = r[c]
            if isinstance(v, (float, np.floating)):
                cells.append("" if not np.isfinite(v) else floatfmt.format(v))
            else:
                cells.append(str(v))
        out.append("| " + " | ".join(cells) + " |")
    return "\n".join(out)


def start_summary(A: pd.DataFrame, D: pd.DataFrame, by=None, baseline="fixed_120") -> pd.DataFrame:
    """Start-algorithm table. Energy/reward are paired against ``baseline`` on the same scenario-day."""
    base = D[D.start == baseline][["scenario", "date", "morning_energy", "morning_reward"]].rename(
        columns={"morning_energy": "e0", "morning_reward": "r0"})
    DD = D.merge(base, on=["scenario", "date"], how="inner")
    DD["de_pct"] = 100.0 * (DD.e0 - DD.morning_energy) / DD.e0.where(DD.e0 > 1e-9)
    DD["de"] = DD.e0 - DD.morning_energy
    DD["dr"] = DD.morning_reward - DD.r0
    keys = ["start"] + ([by] if by else [])
    out = []
    for k, g in A.groupby(keys):
        k = k if isinstance(k, tuple) else (k,)
        dd = DD
        for name, val in zip(keys, k):
            dd = dd[dd[name] == val]
        row = dict(zip(keys, k))
        row.update({
            "AHU-days": len(g),
            "lead p50": q(g.lead, 50), "lead p90": q(g.lead, 90),
            "late % (1F tol)": 100.0 * float((g.late_tol > 0).mean()),
            "late p90 (1F tol)": q(g.late_tol, 90),
            "late %": 100.0 * float((g.late > 0).mean()),
            "late p90 min": q(g.late, 90), "late p99 min": q(g.late, 99),
            "early waste min": float(g.early.mean()),
            "unmet K*min/zone": float(g.unmet.mean()), "unmet p95": q(g.unmet, 95),
            "unmet w/ people K*min/zone": float(g.unmet_people.mean()),
            "prestart run min": float(g.runtime_pre.mean()),
            "energy saved vs fixed120 %": float(np.nanmean(dd.de_pct)) if len(dd) else np.nan,
            "energy saved $/day": float(dd.de.mean()) if len(dd) else np.nan,
            "reward gain vs fixed120": float(dd.dr.mean()) if len(dd) else np.nan,
        })
        out.append(row)
    return pd.DataFrame(out)


def stop_summary(A: pd.DataFrame, D: pd.DataFrame, by=None, baseline="no_early_stop") -> pd.DataFrame:
    # mean per (scenario, date, stop) over runs, then pair with the no-early-stop mean
    g = D.groupby(["scenario", "date", "stop"], as_index=False)[["evening_energy", "evening_reward"]].mean()
    base = g[g.stop == baseline].rename(columns={"evening_energy": "e0", "evening_reward": "r0"}).drop(columns="stop")
    GG = g.merge(base, on=["scenario", "date"])
    GG["de"] = GG.e0 - GG.evening_energy
    GG["de_pct"] = 100.0 * GG.de / GG.e0.where(GG.e0 > 1e-9)
    GG["dr"] = GG.evening_reward - GG.r0
    S = D[["scenario", "date", "season", "post_weekend", "dow", "city"]].drop_duplicates(["scenario", "date"])
    GG = GG.merge(S, on=["scenario", "date"], how="left")
    keys = ["stop"] + ([by] if by else [])
    out = []
    for k, gA in A[~A.stop_other_off].groupby(keys):
        k = k if isinstance(k, tuple) else (k,)
        gg = GG
        for name, val in zip(keys, k):
            gg = gg[gg[name] == val]
        row = dict(zip(keys, k))
        row.update({
            "AHU-days": len(gA),
            "early-stop min mean": float(gA.stop_lead.mean()), "stop p90": q(gA.stop_lead, 90),
            "days stopped %": 100.0 * float((gA.stop_lead > 0).mean()),
            "restarts/day": float(gA.restarts.mean()),
            "unmet K*min/zone": float(gA.stop_unmet.mean()), "unmet p95": q(gA.stop_unmet, 95),
            "max excursion K p95": q(gA.stop_maxdef, 95),
            "energy saved vs no-stop %": float(np.nanmean(gg.de_pct)) if len(gg) else np.nan,
            "energy saved $/day": float(gg.de.mean()) if len(gg) else np.nan,
            "reward gain vs no-stop": float(gg.dr.mean()) if len(gg) else np.nan,
        })
        out.append(row)
    return pd.DataFrame(out)


def _beyond_schedule(anchors, unmet, saved):
    """Energy % saved beyond the fixed-lead schedule curve at equal comfort.

    ``anchors`` = sorted (unmet, saved %) of the fixed-lead runs. The curve is piecewise
    linear between anchors and extended along the end segments.
    """
    pts = [(u, e) for u, e in anchors if np.isfinite(u) and np.isfinite(e)]
    if len(pts) < 2:
        return np.nan
    us = [u for u, _ in pts]
    es = [e for _, e in pts]
    if unmet <= us[0]:
        i = 0
    elif unmet >= us[-1]:
        i = len(us) - 2
    else:
        i = max(k for k in range(len(us) - 1) if us[k] <= unmet)
    du = us[i + 1] - us[i]
    if abs(du) < 1e-9:
        return np.nan
    sched = es[i] + (es[i + 1] - es[i]) * (unmet - us[i]) / du
    return saved - sched


def winner_criteria(P: pd.DataFrame) -> list:
    """Evidence tables used to pick the start winner.

    savings beyond schedule: per scenario, the fixed-lead runs (60/120/180 min) define
    the schedule trade-off curve (energy saved % vs unmet K*min/zone). For each arm, the
    extra energy % it saves compared with a fixed schedule that gives the SAME comfort
    (positive = beats any fixed schedule on the energy-comfort trade-off).
    reward regret: per scenario, the arm's reward gain minus the best arm's (<= 0).
    """
    rows = []
    for sc, g in P.groupby("scenario"):
        g = g.set_index("start")
        anchors = sorted((g.loc[f, "unmet K*min/zone"], g.loc[f, "energy saved vs fixed120 %"])
                         for f in ("fixed_60", "fixed_90", "fixed_120", "fixed_180") if f in g.index)
        best = g["reward gain vs fixed120"].max()
        for st, r in g.iterrows():
            beyond = _beyond_schedule(anchors, r["unmet K*min/zone"], r["energy saved vs fixed120 %"])
            rows.append(dict(scenario=sc, start=st, beyond=beyond,
                             regret=r["reward gain vs fixed120"] - best))
    R = pd.DataFrame(rows)
    if R.empty:
        return []
    n_sc = R.scenario.nunique()
    T = R.groupby("start").agg(scenarios=("scenario", "nunique"),
                               beyond_mean=("beyond", "mean"), beyond_min=("beyond", "min"),
                               regret_mean=("regret", "mean"), regret_worst=("regret", "min"))
    T = T.rename(columns={"beyond_mean": "savings beyond schedule % (mean)",
                          "beyond_min": "savings beyond schedule % (worst scenario)",
                          "regret_mean": "reward regret (mean)", "regret_worst": "reward regret (worst)"})
    T = T.reset_index().sort_values("reward regret (mean)", ascending=False)
    piv = R.pivot(index="scenario", columns="start", values="beyond")
    return ["## Winner criteria (start)", "",
            f"Scenarios: {n_sc}. Arms run on fewer scenarios are not comparable on the worst case.", "",
            md_table(T), "",
            "### Savings beyond a fixed schedule at equal comfort, per scenario (%)", "",
            md_table(piv.reset_index()), ""]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("results", nargs="+")
    ap.add_argument("--out", required=True)
    ap.add_argument("--all-days", action="store_true", help="include the first week (learning warm-up)")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    rows, drows, runs = [], [], []
    for root in a.results:
        for js in sorted(Path(root).rglob("*.json")):
            if js.name.endswith("_jobs.json"):
                continue
            try:
                r, dr, meta = analyze_run(js)
            except Exception as ex:  # keep going; report broken runs
                print("skip", js, ex)
                continue
            if "start" not in meta:
                continue
            scen = f"{meta['building']}/{meta['weather']}"
            tag = dict(scenario=scen, building=meta["building"], weather=meta["weather"],
                       city=city_of(meta["weather"]), start=meta["start"], stop=meta["stop"])
            rows += [dict(tag, **x) for x in r]
            drows += [dict(tag, **x) for x in dr]
            runs.append(dict(tag, score=meta.get("score"), energy=meta.get("energy_cost_total"),
                             steps=meta.get("steps"), n_ahu=meta.get("n_ahu"), n_zones=meta.get("n_zones")))
    A, D, R = pd.DataFrame(rows), pd.DataFrame(drows), pd.DataFrame(runs)
    A.to_csv(out / "ahu_days.csv", index=False)
    D.to_csv(out / "days.csv", index=False)
    R.to_csv(out / "runs.csv", index=False)
    As = A[A.start_ok & (A.day_no >= (0 if a.all_days else WARMUP_DAYS))]
    Ds = D[D.start_ok & (D.day_no >= (0 if a.all_days else WARMUP_DAYS))]
    compact_cols = ["AHU-days", "lead p50", "late % (1F tol)", "late p90 (1F tol)", "unmet K*min/zone",
                    "unmet w/ people K*min/zone", "energy saved vs fixed120 %", "reward gain vs fixed120"]
    parts = ["# Benchmark summary", "",
             f"runs: {len(R)}, scenarios: {R.scenario.nunique()}, buildings: {R.building.nunique()}, "
             f"climates: {R.city.nunique()}, AHU-days (scored): {len(As)}, "
             f"zones per scenario: {int(R.n_zones.min()) if len(R) else 0}-{int(R.n_zones.max()) if len(R) else 0}", ""]
    S = start_summary(As, Ds).sort_values("reward gain vs fixed120", ascending=False)
    parts += ["## Optimal start, all scenarios", "", md_table(S), ""]
    parts += ["## Compact: start by climate", ""]
    Sc = start_summary(As, Ds, "city")
    parts += [md_table(Sc[["start", "city"] + compact_cols].sort_values(["city", "reward gain vs fixed120"], ascending=[True, False])), ""]
    if "season" in As:
        Ss = start_summary(As, Ds, "season")
        parts += ["## Compact: start by season", "",
                  md_table(Ss[["start", "season"] + compact_cols].sort_values(["season", "reward gain vs fixed120"], ascending=[True, False])), ""]
    # equal-weight scenario average (each scenario counts once, whatever its AHU count)
    rows = []
    for sc_name, g in As.groupby("scenario"):
        t = start_summary(g, Ds[Ds.scenario == sc_name])
        t["scenario"] = sc_name
        rows.append(t)
    if rows:
        P = pd.concat(rows)
        W = P.groupby("start")[compact_cols[2:]].mean()
        W["scenarios"] = P.groupby("start").scenario.nunique()
        parts += ["## Start, mean over scenarios (each scenario weighted equally)", "",
                  md_table(W.reset_index().sort_values("reward gain vs fixed120", ascending=False)), ""]
        parts += winner_criteria(P)
    for by in ("season", "post_weekend", "city"):
        parts += [f"## Optimal start by {by}", "", md_table(start_summary(As, Ds, by).sort_values([by, "reward gain vs fixed120"], ascending=[True, False])), ""]
    sc = R.groupby(["scenario", "start"], as_index=False).score.mean().pivot(index="scenario", columns="start", values="score")
    parts += ["## Official episode score per scenario (lower is better)", "", md_table(sc.reset_index(), "{:.5f}"), ""]
    hooked = As[~As.start.isin(["v7", "sac_trim"])]
    hookedD = Ds[~Ds.start.isin(["v7", "sac_trim"])]
    if len(hooked):
        St = stop_summary(hooked, hookedD).sort_values("reward gain vs no-stop", ascending=False)
        parts += ["## Optimal stop (runs with the hooked G36 plant)", "", md_table(St), ""]
        for by in ("season", "city"):
            parts += [f"## Optimal stop by {by}", "", md_table(stop_summary(hooked, hookedD, by)), ""]
    (out / "summary.md").write_text("\n".join(parts))
    print("\n".join(parts[:12]))


if __name__ == "__main__":
    main()
