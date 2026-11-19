"""Local tutorial/research commands. No upload, submission or field-write command."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import sys


def _write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False, default=str) + "\n", encoding="utf-8")


def parser():
    app = argparse.ArgumentParser(description=__doc__)
    sub = app.add_subparsers(dest="command", required=True)
    io = sub.add_parser("iot", help="read timestamped JSONL on stdin; emit native command/status receipts")
    inventory = sub.add_parser("inventory", help="inventory source datasets without inferring missing physical units")
    inventory.add_argument("root", type=Path)
    inventory.add_argument("--out", type=Path, required=True)
    replay = sub.add_parser("replay", help="causal prediction replay; not a closed-loop simulator score")
    replay.add_argument("--data", type=Path, default=Path("data"))
    replay.add_argument("--out", type=Path, required=True)
    replay.add_argument("--tolerance", type=float, default=1.0, help="common observed endpoint tolerance in Fahrenheit")
    replay.add_argument("--selection-window", type=int, default=8, help="explicit research MAE history window; not a BAS guard")
    bundle = sub.add_parser("bundle", help="build an offline Kaggle driver/data bundle, without publishing")
    bundle.add_argument("--project", type=Path, default=Path(__file__).resolve().parents[1])
    bundle.add_argument("--out", type=Path, required=True)
    sim = sub.add_parser("simulate", help="run matched official-kit scenarios with isolated per-AHU controllers")
    sim.add_argument("--kit", type=Path, required=True, help="directory containing smart_buildings/")
    sim.add_argument("--out", type=Path, required=True)
    sim.add_argument("--policies", nargs="+", default=["native"])
    sim.add_argument("--steps", type=int, default=8640, help="8640 for a full 30-day episode; shorter is smoke only")
    sim.add_argument("--workers", type=int, default=2)
    sim.add_argument("--phase", choices=["both", "start", "stop"], default="both")
    sim.add_argument("--limit", type=int, help="explicit scenario limit, omitted means all discovered scenarios")
    sim.add_argument("--no-resume", action="store_true")
    sim.add_argument("--sample-fraction", type=float, default=0.3)
    sim.add_argument("--seed", type=int, default=0)
    sim.add_argument("--shard-index", type=int)
    sim.add_argument("--shard-count", type=int)
    sim.add_argument("--list", action="store_true", help="print discovered scenario inventory without loading simulator")
    return app


def main(argv=None):
    args = parser().parse_args(argv)
    if args.command == "iot":
        from .iot import run_jsonl
        return run_jsonl(sys.stdin, sys.stdout)
    if args.command == "inventory":
        from .datasets import inventory_datasets
        result = inventory_datasets(args.root)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        _write_json(args.out, result)
        print(json.dumps({"candidate_files": result["candidate_files"], "counts": result["counts"], "out": str(args.out)}))
        return 0
    if args.command == "replay":
        from .replay import ResearchSelector, load_recovery_events, run_replay
        events = load_recovery_events(args.data, allowable_deviation=args.tolerance)
        result = run_replay(events, selector=ResearchSelector(window=args.selection_window,
                                                            cold_start_model="native_minutes_per_degree"))
        args.out.mkdir(parents=True, exist_ok=True)
        _write_json(args.out / "summary.json", result.summary())
        _write_json(args.out / "selection.json", result.selection_records)
        _write_json(args.out / "error_history.json", result.error_history)
        with (args.out / "records.jsonl").open("w", encoding="utf-8") as stream:
            for record in result.records:
                stream.write(json.dumps(record, allow_nan=False, default=str) + "\n")
        print(json.dumps({"events": len(events), "records": len(result.records), "out": str(args.out),
                          "scope": "recorded recovery prediction; no closed-loop score"}))
        return 0
    if args.command == "bundle":
        from .bundle import build_bundle
        result = build_bundle(args.project, args.out)
        print(json.dumps({"out": str(args.out), "assets": list(result["assets"])}))
        return 0
    if args.command == "simulate":
        from .simulation import discover_scenarios, run_matrix
        if args.list:
            print(json.dumps(discover_scenarios(args.kit), indent=2, default=str))
            return 0
        result = run_matrix(args.kit, args.out, policies=tuple(args.policies), steps=args.steps,
                            workers=args.workers, phase=args.phase, resume=not args.no_resume,
                            limit=args.limit, sample_fraction=args.sample_fraction, seed=args.seed,
                            shard_index=args.shard_index, shard_count=args.shard_count)
        print(json.dumps(result, indent=2, default=str))
        return 0 if not result.get("failed", 0) else 1
    return 2
