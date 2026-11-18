from pathlib import Path

from hvac_optimal.tutorial import find_data, reference_learning_demo


def test_all_four_reference_demo_updates_are_native_partial_responses():
    rows = reference_learning_demo()
    assert len(rows) == 4
    assert len({row["parameter"] for row in rows}) == 4
    assert all(row["target_reached"] is False for row in rows)
    assert all(row["new_minutes_per_degree"] != row["old_minutes_per_degree"] for row in rows)


def test_versioned_recovery_dataset_is_complete_and_checked():
    root = Path(__file__).resolve().parents[1]
    assert find_data(root) == root / "data"
