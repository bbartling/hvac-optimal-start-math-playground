from pathlib import Path
import json
import subprocess
import sys

from hvac_optimal.bundle import build_bundle
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


def test_notebook_controller_example_runs_without_site_packages(tmp_path):
    root = Path(__file__).resolve().parents[1]
    notebook = json.loads((root / "optimal_start_stop_tutorial.ipynb").read_text(encoding="utf-8"))
    cells = [c for c in notebook["cells"] if "stdlib-controller" in c.get("metadata", {}).get("tags", [])]
    assert len(cells) == 1
    source = "".join(cells[0]["source"])
    build_bundle(root, tmp_path / "bundle")
    archive = tmp_path / "bundle" / "hvac_optimal_driver.zip"
    verification = (
        "import sys;sys.path.insert(0,sys.argv[1]);ns={};exec(sys.argv[2],ns);"
        "e=next(e for e in ns['result'].events if e['type']=='native_learning');"
        "assert e['parameter']=='runtime_per_degree_heating';"
        "assert e['temperature_change']>0 and not e['target_reached'];"
        "assert not {'numpy','pandas','matplotlib'}.intersection(sys.modules)"
    )
    result = subprocess.run([sys.executable, "-S", "-c", verification, str(archive), source],
                            cwd=tmp_path, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
