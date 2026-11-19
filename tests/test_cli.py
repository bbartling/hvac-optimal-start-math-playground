import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def test_help_runs_without_optional_libraries():
    result = subprocess.run([sys.executable, "-S", "-m", "hvac_optimal", "--help"], cwd=ROOT,
                            text=True, capture_output=True)
    assert result.returncode == 0
    assert "simulate" in result.stdout and "iot" in result.stdout


def test_cli_replays_every_bundled_event_without_site_packages(tmp_path):
    result = subprocess.run([sys.executable, "-S", "-m", "hvac_optimal", "replay", "--data", str(ROOT / "data"),
                             "--out", str(tmp_path)], cwd=ROOT, text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    receipt = json.loads(result.stdout)
    assert receipt["events"] == 1163
    assert receipt["records"] == 9304
    summaries = json.loads((tmp_path / "summary.json").read_text())
    assert len(summaries) == 8
    assert all(x["events"] == 1163 for x in summaries)
