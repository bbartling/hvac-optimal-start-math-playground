from unittest.mock import patch

import pytest

from hvac_optimal.simulator_setup import preflight, resolve_kit


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
