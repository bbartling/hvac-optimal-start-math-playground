"""Read-only dataset discovery without pandas, numpy, simulator imports or network.

Inventory identifies what each artifact can establish. RL feature arrays,
geometry and aggregate scores are never relabelled as physical recoveries.
"""
from __future__ import annotations

import ast
import csv
import gzip
import json
import os
import re
import struct
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


_EXTENSIONS = {".csv", ".npz", ".npy", ".json", ".jsonl", ".parquet", ".gin"}
_SKIP = {".git", "__pycache__", "node_modules", ".pytest_cache", ".mypy_cache", ".ruff_cache"}


def _files(root: Path):
    for directory, directories, filenames in os.walk(root):
        directories[:] = sorted(name for name in directories
                                if name not in _SKIP and not name.startswith((".venv", "venv")))
        for name in sorted(filenames):
            path = Path(directory) / name
            if path.suffix.lower() in _EXTENSIONS or name.lower().endswith(".csv.gz"):
                yield path


def _npy_header(stream) -> dict[str, Any]:
    """Read only the documented .npy header; never unpickle an object array."""
    if stream.read(6) != b"\x93NUMPY":
        raise ValueError("not a NPY file")
    major, minor = stream.read(2)
    if major == 1:
        length = struct.unpack("<H", stream.read(2))[0]
    elif major in (2, 3):
        length = struct.unpack("<I", stream.read(4))[0]
    else:
        raise ValueError(f"unsupported NPY version {major}.{minor}")
    header = ast.literal_eval(stream.read(length).decode("utf-8" if major == 3 else "latin1"))
    return dict(shape=list(header["shape"]), dtype=header["descr"], fortran_order=header["fortran_order"])


def discover_scenarios(root: str | Path, *, include_evaluation: bool = False) -> list[dict[str, Any]]:
    """Discover scenario configuration paths and geometry, without running them.

    Accept the sibling repository, .kit, or smart_buildings directory. Training
    and evaluation copies are distinct records when evaluation is requested.
    Counts come from the filesystem and are never assumed from a manifest.
    """
    root = Path(root).resolve()
    records = []
    allowed = {"training_scenarios", "evaluation_scenarios"} if include_evaluation else {"training_scenarios"}
    for path in _files(root):
        if path.name != "config.gin" or not allowed.intersection(path.parts):
            continue
        text = path.read_text(encoding="utf-8-sig")
        match = re.search(r"^\s*weather_csv_path\s*=\s*['\"]([^'\"]+)['\"]", text, re.MULTILINE)
        records.append(dict(scenario=f"{path.parent.parent.name}/{path.parent.name}",
                            split=next(part for part in path.parts if part in allowed),
                            building=path.parent.parent.name, weather=path.parent.name,
                            config=str(path), weather_csv=match.group(1) if match else None,
                            floor_plan=str(path.parent / "floor_plan.npy"),
                            zone_map=str(path.parent / "zone_map.npy"),
                            geometry_complete=all((path.parent / name).is_file() for name in ("floor_plan.npy", "zone_map.npy")),
                            use="simulator_input", recovery_truth=False))
    return sorted(records, key=lambda row: (row["split"], row["scenario"]))


def _classify(path: Path) -> dict[str, Any]:
    item: dict[str, Any] = dict(category="metadata", usable_for_recovery=False,
                                reason="metadata has no measured temperature trajectory with an endpoint")
    lower = path.name.lower()
    if path.suffix == ".gin":
        return dict(item, category="scenario_config", reason="configuration describes simulator inputs, not observed outcomes")
    if path.suffix == ".npy":
        with path.open("rb") as stream:
            metadata = _npy_header(stream)
        geometry = path.name in {"floor_plan.npy", "zone_map.npy"}
        return dict(item, category="geometry_array" if geometry else "unknown_array", array=metadata,
                    reason="geometry/zone map has no time or recovery-temperature labels" if geometry else
                    "array shape/dtype do not establish physical quantities, units or recovery endpoints")
    if path.suffix == ".npz":
        with zipfile.ZipFile(path) as archive:
            arrays = {}
            for member in archive.namelist():
                if member.endswith(".npy"):
                    with archive.open(member) as stream:
                        arrays[member[:-4]] = _npy_header(stream)
        keys = set(arrays)
        if {"feats", "acts", "rews"} <= keys:
            return dict(item, category="rl_rollout", arrays=arrays,
                        reason="normalized policy features/actions/rewards lack raw zone temperatures, timestamps and comfort endpoints")
        if {"tz", "oat", "ts"} <= keys:
            return dict(item, category="physical_trace_requires_adapter", arrays=arrays,
                        reason="potential physical trace; units, schedule, AHU mapping and generating-controller provenance require an explicit adapter")
        return dict(item, category="unknown_array_archive", arrays=arrays,
                    reason="array names alone do not establish physical units or recovery labels")
    if path.suffix == ".parquet":
        return dict(item, category="uninspected_parquet", reason="no stdlib Parquet adapter; physical units and recovery endpoint unverified")
    if path.suffix == ".csv" or lower.endswith(".csv.gz"):
        opener = gzip.open if lower.endswith(".gz") else open
        with opener(path, "rt", encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            columns = reader.fieldnames or []
            count = sum(1 for _ in reader)
        item.update(columns=columns, rows=count)
        keys = set(columns)
        if {"event", "minute", "temp_f"} <= keys:
            return dict(item, category="recovery_trajectory", usable_for_recovery=True, units="degF, minute",
                        reason="observed samples; requires paired event metadata for initial state and endpoint")
        if {"event", "scenario", "ahu", "start_temp_f", "target_f", "minutes_to_target"} <= keys:
            return dict(item, category="recovery_events", usable_for_recovery=True, units="degF, minute",
                        reason="bundled simulator event metadata; censored exact-target durations retained; requires paired trajectories")
        if {"timestamp_utc", "zone_id", "temp_f", "mode", "event_id"} <= keys:
            return dict(item, category="synthetic_rate_history" if "synthetic" in lower else "temperature_history_requires_provenance",
                        units="degF, UTC timestamps", usable_for_rate_learning="synthetic" in lower,
                        reason="temperature changes and elapsed times available, but no target/setpoint/OAT; cannot score time-to-comfort")
        if {"Time", "TempC"} <= keys or "weather" in path.parts:
            return dict(item, category="weather_history", units="use named CSV temperature/time columns",
                        reason="outdoor weather only; no zone response or HVAC event")
        if {"start", "time", "zmin_f", "zmean_f", "zmax_f"} <= keys:
            return dict(item, category="aggregate_morning_example", units="degF, local recorded timestamps",
                        reason="aggregate min/mean/max lacks a stable per-zone trajectory and start/target metadata")
        if any(key in keys for key in ("score", "reward", "morning_reward", "stop_unmet", "late_tol", "kwh_per_zone")):
            return dict(item, category="aggregate_results", reason="aggregate/control-dependent metrics cannot reconstruct a measured recovery")
        return dict(item, category="unmapped_csv", reason="no declared physical-recovery schema; no unit inference")
    if path.suffix in {".json", ".jsonl"}:
        with path.open(encoding="utf-8-sig") as stream:
            if path.suffix == ".jsonl":
                keys, rows = set(), 0
                for line in stream:
                    if line.strip():
                        value = json.loads(line)
                        rows += 1
                        if isinstance(value, dict):
                            keys.update(value)
                item.update(rows=rows, keys=sorted(keys))
                return dict(item, category="episode_score_log" if {"building", "weather", "score"} <= keys else "unmapped_jsonl",
                            reason="episode summaries contain no raw recovery-temperature/time labels" if "score" in keys else
                            "no declared temperature/endpoint schema; explicit adapter required")
            value = json.load(stream)
        keys = list(value) if isinstance(value, dict) else []
        item["keys"] = keys
        if isinstance(value, dict) and "layers" in value and "n_feat" in value:
            return dict(item, category="policy_weights", reason="model weights/feature normalization are not physical recovery observations")
        return dict(item, category="result_or_configuration_json", reason="scores, fitted rates and configuration cannot substitute for their generating temperature histories")
    return item


def inventory_datasets(root: str | Path) -> dict[str, Any]:
    """Inventory every candidate data artifact under root, including unusable files.

    Source code, dependency environments, git internals and cache directories are
    excluded. Failed inspection remains visible with its exception type/reason.
    Does not read array payloads or execute configuration, pickle or simulator code.
    """
    root = Path(root).resolve()
    items = []
    for path in _files(root):
        base = dict(path=str(path), relative_path=path.relative_to(root).as_posix(), bytes=path.stat().st_size)
        try:
            base.update(_classify(path))
        except (OSError, ValueError, KeyError, SyntaxError, EOFError, struct.error, zipfile.BadZipFile) as exc:
            base.update(category="inspection_error", usable_for_recovery=False,
                        reason=f"{type(exc).__name__}: {exc}")
        items.append(base)
    counts = Counter(item["category"] for item in items)
    return dict(root=str(root), exists=root.exists(), candidate_files=len(items), counts=dict(sorted(counts.items())),
                usable_recovery_files=sum(item["usable_for_recovery"] for item in items),
                unusable_recovery_files=sum(not item["usable_for_recovery"] for item in items),
                training_scenarios=discover_scenarios(root), items=items,
                exclusions="git internals, dependency environments, node_modules, bytecode/test/tool caches, source code; no physical values inferred from normalized RL arrays")
