"""Small presentation helpers; plotting libraries remain optional imports."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import gzip
import json
from pathlib import Path

from .reference import Inputs, OptimizedStartStop


def find_data(search_root=None):
    """Find a complete versioned recovery dataset, with no network fallback."""
    base = Path.cwd() if search_root is None else Path(search_root)
    candidates = [base / "data", base.parent / "data"]
    kaggle = Path("/kaggle/input")
    if kaggle.exists():
        candidates.extend(p.parent for p in sorted(kaggle.rglob("recovery_manifest.json")))
    for path in candidates:
        manifest_path = path / "recovery_manifest.json"
        if not manifest_path.is_file():
            continue
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for name, expected in manifest["sha256"].items():
            asset = path / name
            if not asset.is_file() or hashlib.sha256(asset.read_bytes()).hexdigest() != expected:
                raise ValueError(f"missing or changed recovery dataset asset: {name}")
        return path
    raise FileNotFoundError("Attach the offline tutorial dataset (driver zip + data/recovery_manifest.json).")


def reference_learning_demo():
    """Four declared partial-response fixtures, not a physical simulation.

    Each case changes schedule before the full comfort crossing. Small positive
    responses still update exactly as in the supplied BAS learning branches.
    """
    cases = [
        ("heating start", "start", 66.0, 66.2, False),
        ("cooling start", "start", 80.0, 79.5, True),
        ("heating stop", "stop", 70.0, 69.5, False),
        ("cooling stop", "stop", 75.0, 75.5, True),
    ]
    rows = []
    for label, kind, beginning, end, cooling in cases:
        controller = OptimizedStartStop()
        starting = kind == "start"
        hour = 5 if starting else 17
        now = datetime(2026, 11, 18, hour, 50, 15, tzinfo=timezone.utc)
        boundary = now.replace(hour=6 if starting else 18, minute=0, second=0)
        controller.tick(Inputs(space_temp=beginning, outside_temp=40, start_enable=True, stop_enable=True,
                               schedule_status=not starting, next_event_time=boundary,
                               next_event_value=starting, heat_cool_mode=cooling), now=now)
        result = controller.tick(Inputs(space_temp=end, outside_temp=40, start_enable=True, stop_enable=True,
                                        schedule_status=starting,
                                        next_event_time=boundary.replace(hour=18) if starting else boundary.replace(day=19, hour=6),
                                        next_event_value=not starting, heat_cool_mode=cooling),
                                 now=boundary.replace(second=15))
        for event in result.events:
            if event["type"] == "native_learning":
                rows.append({"case": label, **deepcopy(event)})
    return rows


def plot_replay_summary(result):
    import matplotlib.pyplot as plt
    rows = sorted(result.summary(), key=lambda r: r["common_mae"] if r["common_mae"] is not None else float("inf"))
    names = [r["model"].replace("pnnl_", "").replace("_", " ") for r in rows]
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.4))
    axes[0].barh(names, [r["common_mae"] if r["common_mae"] is not None else float("nan") for r in rows], color="#267c9c")
    axes[0].invert_yaxis()
    axes[0].set(xlabel="MAE on common assessed events (minutes)", title="Same endpoint, same cohort; no prediction cap")
    axes[1].barh(names, [r["assessed"] for r in rows], color="#61b59b", label="assessed")
    axes[1].barh(names, [r["unassessed"] for r in rows], left=[r["assessed"] for r in rows],
                 color="#c9d1d9", label="unassessed / censored")
    axes[1].invert_yaxis()
    axes[1].set(xlabel="Recorded events", title="Missing evidence stays visible")
    axes[1].legend(loc="upper center", bbox_to_anchor=(.5, -.16), ncol=2)
    fig.tight_layout(rect=(0, .06, 1, 1))
    return fig


def plot_error_history(result):
    import matplotlib.pyplot as plt
    import pandas as pd
    history = pd.DataFrame(result.error_history)
    # A single AHU has its own learner history: do not join unrelated buildings
    # into a fictitious online trajectory.
    group = history.groupby(["scenario", "ahu"], sort=True).size().idxmax()
    selected = history[(history.scenario == group[0]) & (history.ahu == group[1])]
    decisions = pd.DataFrame(result.records)
    decisions = decisions[(decisions.scenario == group[0]) & (decisions.ahu == group[1])]
    event_ids = list(dict.fromkeys(decisions.event))
    fig, ax = plt.subplots(figsize=(11, 4.2))
    for name, rows in selected.groupby("model", sort=False):
        errors = rows.set_index("event").absolute_error.reindex(event_ids)
        ax.plot(range(1, len(event_ids) + 1), errors.rolling(8, min_periods=1).mean(),
                label=name.replace("pnnl_", "").replace("_", " "), linewidth=1.6)
    ax.set(xlabel="Same decision-event index for every model on this AHU", ylabel="Trailing 8-decision-event MAE (min)",
           title=f"Learning over time — {group[0]}, {group[1]}")
    ax.legend(ncol=2, fontsize=8, bbox_to_anchor=(1.01, 1), loc="upper left")
    fig.tight_layout()
    return fig


def plot_selection(result):
    import matplotlib.pyplot as plt
    import pandas as pd
    selection = pd.DataFrame(result.selection_records)
    group = selection.groupby(["scenario", "ahu"], sort=True).size().idxmax()
    subset = selection[(selection.scenario == group[0]) & (selection.ahu == group[1])]
    names = list(dict.fromkeys(subset.model.fillna("no prediction")))
    positions = {name: i for i, name in enumerate(names)}
    fig, ax = plt.subplots(figsize=(11, 3.6))
    ax.step(range(1, len(subset) + 1), [positions[name] for name in subset.model.fillna("no prediction")],
            where="post", color="#bc6c25", linewidth=2)
    ax.set_yticks(range(len(names)), [name.replace("_", " ") for name in names])
    ax.set(xlabel="Decision event", title=f"Research selector: past common-cohort MAE only — {group[0]}, {group[1]}")
    fig.tight_layout()
    return fig


def simulation_table(manifest):
    """Compact actual-run evidence; failed jobs remain visible."""
    rows = []
    for job in manifest["results"]:
        base = {"scenario": job["scenario"]["scenario_id"], "policy": job["policy"],
                "status": job["status"], "steps": job.get("steps_completed", 0),
                "score_scope": job.get("score_status", "unavailable")}
        for ahu in job.get("ahus", []):
            rows.append({**base, "ahu": ahu["ahu_id"],
                         "native_updates": ahu["native_learning_events"],
                         "accepted_research_fits": ahu["accepted_research_fits"]})
        if not job.get("ahus"):
            rows.append(base)
    return rows


def plot_ahu_trace(history_path, ahu_id=None):
    """Plot one actual AHU's temperatures, run command and learned parameters."""
    import matplotlib.pyplot as plt
    import pandas as pd
    with gzip.open(history_path, "rt", encoding="utf-8") as stream:
        header = json.loads(next(stream))
        rows = []
        for line in stream:
            row = json.loads(line)
            if row.get("type") != "ahu_tick":
                continue
            if ahu_id is None:
                ahu_id = row["ahu_id"]
            if row["ahu_id"] == ahu_id:
                rows.append(row)
    if not rows:
        raise ValueError("no ticks for the requested AHU")
    times = pd.to_datetime([row["time"] for row in rows], utc=True)
    fig, axes = plt.subplots(3, 1, figsize=(12, 8), sharex=True)
    axes[0].plot(times, [r["sample_temperature_f"] for r in rows], label="fixed zone sample")
    axes[0].plot(times, [r["outside_temperature_f"] for r in rows], label="outside", alpha=.65)
    if "comfort_window_f" in header:
        axes[0].axhspan(*header["comfort_window_f"], color="#61b59b", alpha=.15, label="occupied comfort band")
    axes[0].set(ylabel="Temperature (°F)", title=f"Actual simulator trace — {header['scenario']['scenario_id']}, {ahu_id}")
    for key, label in (("occupied", "scheduled occupied"), ("allowed_run", "AHU run allowed")):
        axes[1].step(times, [int(r[key]) for r in rows], where="post", label=label)
    axes[1].set(ylabel="Command / schedule", yticks=[0, 1])
    for name in ("runtime_per_degree_heating", "runtime_per_degree_cooling",
                 "drifttime_per_degree_heating", "drifttime_per_degree_cooling"):
        axes[2].plot(times, [r["state"][name] for r in rows], label=name.replace("_per_degree", "").replace("_", " "))
    axes[2].set(ylabel="Learned minutes / °F", xlabel="Time (UTC; schedule timezone is recorded in receipt)")
    for ax in axes:
        ax.legend(fontsize=8, loc="upper left", bbox_to_anchor=(1.01, 1))
    fig.tight_layout()
    return fig
