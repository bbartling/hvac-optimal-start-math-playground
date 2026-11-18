import io
import json
import struct
import zipfile
from pathlib import Path

from hvac_optimal.datasets import discover_scenarios, inventory_datasets


def npy_bytes(shape=(2, 3), dtype="<f4"):
    header = repr(dict(descr=dtype, fortran_order=False, shape=shape)).encode("latin1") + b"\n"
    return b"\x93NUMPY\x01\x00" + struct.pack("<H", len(header)) + header


def test_inventory_discovers_dynamic_counts_and_does_not_mislabel_rl_as_truth(tmp_path):
    chunks = tmp_path / "results" / "chunks"
    chunks.mkdir(parents=True)
    for index in range(2):
        with zipfile.ZipFile(chunks / f"episode{index}.npz", "w") as archive:
            for name in ("feats", "acts", "rews", "score", "steps"):
                archive.writestr(name + ".npy", npy_bytes())
    inventory = inventory_datasets(tmp_path)
    assert inventory["counts"] == {"rl_rollout": 2}
    assert inventory["usable_recovery_files"] == 0
    assert inventory["items"][0]["arrays"]["feats"]["shape"] == [2, 3]


def test_discover_scenarios_finds_all_training_and_optional_evaluation_copies(tmp_path):
    for split, scenario in (("training_scenarios", "cold_1"), ("training_scenarios", "warm_2"),
                            ("evaluation_scenarios", "cold_1")):
        directory = tmp_path / ".kit" / "smart_buildings" / split / "building_1" / scenario
        directory.mkdir(parents=True)
        (directory / "config.gin").write_text("weather_csv_path = 'weather/cold.csv'\n")
        (directory / "floor_plan.npy").write_bytes(npy_bytes())
        (directory / "zone_map.npy").write_bytes(npy_bytes())
    records = discover_scenarios(tmp_path)
    assert len(records) == 2 and all(row["geometry_complete"] for row in records)
    assert len(discover_scenarios(tmp_path, include_evaluation=True)) == 3
    assert records[0]["weather_csv"] == "weather/cold.csv"


def test_synthetic_temperature_history_has_rates_but_no_target_truth(tmp_path):
    (tmp_path / "synthetic_recovery_events.csv").write_text(
        "timestamp_utc,zone_id,temp_f,mode,event_id\n2026-01-01T00:00:00Z,z1,65,heating,1\n")
    item = inventory_datasets(tmp_path)["items"][0]
    assert item["category"] == "synthetic_rate_history"
    assert item["usable_for_rate_learning"] and not item["usable_for_recovery"]
    assert "no target" in item["reason"]


def test_unknown_array_units_are_not_guessed_and_broken_files_stay_visible(tmp_path):
    (tmp_path / "unknown.npy").write_bytes(npy_bytes(dtype="|O"))
    (tmp_path / "broken.npz").write_bytes(b"not an archive")
    inventory = inventory_datasets(tmp_path)
    assert inventory["counts"] == {"unknown_array": 1, "inspection_error": 1}
    assert inventory["unusable_recovery_files"] == 2


def test_episode_jsonl_scores_are_counted_without_fabricating_recoveries(tmp_path):
    path = tmp_path / "episodes.jsonl"
    path.write_text("\n".join(json.dumps(dict(building="one", weather="cold", score=index)) for index in range(3)))
    item = inventory_datasets(tmp_path)["items"][0]
    assert item["rows"] == 3 and item["category"] == "episode_score_log"
    assert not item["usable_for_recovery"]


def test_dependency_and_git_data_are_excluded(tmp_path):
    for folder in (".git", ".venv-sim", "node_modules"):
        directory = tmp_path / folder
        directory.mkdir()
        (directory / "ignored.json").write_text("{}")
    assert inventory_datasets(tmp_path)["candidate_files"] == 0
