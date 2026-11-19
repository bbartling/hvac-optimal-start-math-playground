from unittest.mock import patch
import json
import os
from types import SimpleNamespace

import pytest

from hvac_optimal.simulator_setup import preflight, resolve_kit
import hvac_optimal.simulator_setup as setup


def test_discovers_repository_kit_from_nested_working_directory(tmp_path, monkeypatch):
    kit = tmp_path / '.kit' / 'smart_buildings'
    kit.mkdir(parents=True)
    (kit / 'evaluate.py').touch()
    nested = tmp_path / 'notebooks'
    nested.mkdir()
    monkeypatch.chdir(nested)
    assert resolve_kit() == tmp_path / '.kit'


def test_explicit_missing_kit_does_not_silently_use_another(tmp_path):
    with pytest.raises(FileNotFoundError):
        resolve_kit(tmp_path / 'missing')


def test_missing_dependency_is_reported_before_worker_launch():
    with patch('hvac_optimal.simulator_setup.importlib.util.find_spec', return_value=None):
        with pytest.raises(RuntimeError, match='gin-config.*HVAC Optimal Start Simulator'):
            preflight()


def test_notebook_uses_project_python_instead_of_current_kernel(tmp_path, monkeypatch):
    root = tmp_path / 'project'
    local = root / '.venv-sim' / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
    local.parent.mkdir(parents=True)
    local.touch()
    monkeypatch.setattr(setup, '__file__', str(root / 'hvac_optimal/simulator_setup.py'))
    out = tmp_path / 'run'

    def child(command, **kwargs):
        assert command[0] == str(local)
        assert command[command.index('--steps') + 1] == '360'
        assert command[command.index('--limit') + 1] == '1'
        out.mkdir()
        (out / 'manifest.json').write_text(json.dumps({'complete': 1, 'failed': 0}))
        return SimpleNamespace(returncode=0)

    with patch.object(setup.subprocess, 'run', side_effect=child):
        assert setup.run_notebook_matrix(root / '.kit', out)['complete'] == 1
