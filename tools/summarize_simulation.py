"""Audit completed matched simulator jobs and export compact reproducible evidence.

Outputs belong in TEMP; copy only the small reviewed summary into docs/validation.
Raw simulator reward is higher-is-better, not an official leaderboard score.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import statistics


def summarize(manifest):
    jobs = manifest["results"]
    if manifest["status"] != "complete" or manifest["failed"] or manifest["pending"]:
        raise ValueError("matrix is incomplete or contains failed jobs")
    if len(jobs) != manifest["job_count"] or any(j["status"] != "complete" for j in jobs):
        raise ValueError("manifest count/status does not match receipts")
    if any(j["steps_completed"] != j["steps"] for j in jobs):
        raise ValueError("actual completed horizon differs from requested horizon")
    if any(not math.isfinite(j["mean_reward"]) for j in jobs):
        raise ValueError("nonfinite reward")
    grouped = defaultdict(dict)
    for job in jobs:
        key = job["scenario"]["scenario_id"]
        if job["policy"] in grouped[key]:
            raise ValueError("duplicate scenario/policy receipt")
        grouped[key][job["policy"]] = job
    policies = sorted({j["policy"] for j in jobs})
    for group in grouped.values():
        if set(group) != set(policies):
            raise ValueError("unmatched policy/scenario matrix")
        first = next(iter(group.values()))
        for job in group.values():
            if any(job[key] != first[key] for key in ("phase", "steps", "seed", "sample_fraction", "zone_weights")):
                raise ValueError("unmatched experimental settings")
            left = {a["ahu_id"]: a["sampling"] for a in first["ahus"]}
            right = {a["ahu_id"]: a["sampling"] for a in job["ahus"]}
            if left != right:
                raise ValueError("AHU mapping or sample differs between policy arms")
    metrics = {}
    for policy in policies:
        selected = [j for j in jobs if j["policy"] == policy]
        totals = defaultdict(Counter)
        for job in selected:
            for ahu in job["ahus"]:
                common_counts = {m["common_assessed"] for m in ahu["metrics"].values()}
                if len(common_counts) != 1:
                    raise ValueError("models have mismatched common-cohort counts")
                for name, metric in ahu["metrics"].items():
                    for key in ("assessed", "unassessed", "unsupported", "common_assessed",
                                "common_absolute_error_sum"):
                        totals[name][key] += metric[key]
        metrics[policy] = {
            "jobs": len(selected), "ahu_runs": sum(len(j["ahus"]) for j in selected),
            "mean_raw_reward": statistics.mean(j["mean_reward"] for j in selected),
            "native_learning_events": sum(a["native_learning_events"] for j in selected for a in j["ahus"]),
            "accepted_research_fits": sum(a["accepted_research_fits"] for j in selected for a in j["ahus"]),
            "zero_native_update_ahu_runs": sum(a["native_learning_events"] == 0 for j in selected for a in j["ahus"]),
            "shadow_metrics": {name: {**dict(counts),
                "common_mae_minutes": counts["common_absolute_error_sum"] / counts["common_assessed"]
                    if counts["common_assessed"] else None} for name, counts in sorted(totals.items())},
        }
    pairs = []
    if set(policies) == {"native", "winner"}:
        for scenario, group in sorted(grouped.items()):
            native, winner = group["native"], group["winner"]
            pairs.append({"scenario": scenario, "building": native["scenario"]["building"],
                          "native_mean_raw_reward": native["mean_reward"],
                          "winner_mean_raw_reward": winner["mean_reward"],
                          "reward_difference_winner_minus_native": winner["mean_reward"] - native["mean_reward"]})
    buildings = []
    for building in sorted({j["scenario"]["building"] for j in jobs}):
        row = {"building": building}
        for policy in policies:
            selected = [j for j in jobs if j["scenario"]["building"] == building and j["policy"] == policy]
            row[policy + "_jobs"] = len(selected)
            row[policy + "_mean_raw_reward"] = statistics.mean(j["mean_reward"] for j in selected)
        buildings.append(row)
    return {
        "format_version": 1, "generated_utc": datetime.now(timezone.utc).isoformat(),
        "run_signature": manifest["signature"], "complete": len(jobs), "failed": 0,
        "all_full_horizon": all(j["steps_completed"] == 8640 for j in jobs),
        "steps_per_job": dict(Counter(str(j["steps_completed"]) for j in jobs)),
        "simulator_steps_total": sum(j["steps_completed"] for j in jobs),
        "ahu_ticks_total": sum(j["steps_completed"] * len(j["ahus"]) for j in jobs),
        "scenarios": len(grouped), "buildings": buildings,
        "ahu_runs": sum(len(j["ahus"]) for j in jobs),
        "independent_scenario_ahu_pairs": len({(j["scenario"]["scenario_id"], a["ahu_id"]) for j in jobs for a in j["ahus"]}),
        "reward_scope": "local raw simulator reward; higher is better; single seed; not an official leaderboard score",
        "simulator_recirculation_caps": dict(Counter(str(j["simulator_recirculation_cap"]) for j in jobs)),
        "sample_fallbacks": dict(Counter(a["sampling"]["fallback_reason"] or "none" for j in jobs for a in j["ahus"])),
        "policies": metrics, "paired_scenarios": pairs,
        "winner_better_scenarios": sum(p["reward_difference_winner_minus_native"] > 0 for p in pairs),
        "winner_worse_scenarios": sum(p["reward_difference_winner_minus_native"] < 0 for p in pairs),
        "limitations": ["No full-return-air simulation: observed maximum recirculation is 70%.",
                        "Five-minute adapter cadence differs from minute scans in the supplied Java.",
                        "Common cohorts are matched within each policy trajectory, not across different controller arms.",
                        "Shadow-model MAE does not measure counterfactual controlled energy or comfort.",
                        "Configured scenarios and one fixed seed per matched comparison; no uncertainty estimate."],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    result = summarize(json.loads(args.manifest.read_text(encoding="utf-8")))
    result["input_manifest_sha256"] = hashlib.sha256(args.manifest.read_bytes()).hexdigest()
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "simulation_summary.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["paired_scenarios"]:
        with (args.out / "paired_scenarios.csv").open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=result["paired_scenarios"][0].keys())
            writer.writeheader()
            writer.writerows(result["paired_scenarios"])
    print(json.dumps({key: result[key] for key in ("complete", "scenarios", "ahu_runs", "all_full_horizon",
                                                   "winner_better_scenarios", "winner_worse_scenarios")}))


if __name__ == "__main__":
    main()
