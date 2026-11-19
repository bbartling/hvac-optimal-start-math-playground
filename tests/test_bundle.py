import importlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile

from hvac_optimal.bundle import build_bundle


def test_offline_bundle_contains_driver_and_data_and_runs_without_site_packages(tmp_path):
    root = Path(__file__).resolve().parents[1]
    manifest = build_bundle(root, tmp_path / "bundle")
    archive = tmp_path / "bundle" / "hvac_optimal_driver.zip"
    with zipfile.ZipFile(archive) as zipped:
        names = zipped.namelist()
        assert "hvac_optimal/reference.py" in names
        assert "hvac_optimal/models.py" in names
        assert not any(n.endswith(".java") for n in names)
    assert len(manifest["assets"]) == 5
    notebook = json.loads((tmp_path / 'bundle' / 'optimal_start_stop_tutorial.ipynb').read_text(encoding='utf-8'))
    assert notebook['metadata']['kernelspec']['name'] == 'python3'
    assert any('RUN_OFFICIAL_SIMULATOR = False' in ''.join(cell['source']) for cell in notebook['cells'])
    result = subprocess.run([sys.executable, "-S", "-c",
        "import sys;sys.path.insert(0,sys.argv[1]);from hvac_optimal.reference import OptimizedStartStop;"
        "from hvac_optimal.models import default_models;print(len(default_models()))", str(archive)],
        cwd=tmp_path, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert int(result.stdout.strip()) >= 6
