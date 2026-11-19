"""Standard-library-only discovery and diagnostics for optional simulator use."""
import importlib.util
from pathlib import Path
import sys


def resolve_kit(explicit=None):
    if explicit is not None:
        candidates = [Path(explicit).expanduser().resolve()]
    else:
        candidates = [p / '.kit' for p in (Path.cwd(), *Path.cwd().parents)]
        kaggle = Path('/kaggle/input')
        if kaggle.is_dir():
            candidates.extend(p.parent.parent for p in kaggle.rglob('smart_buildings/training_scenarios'))
    for path in candidates:
        if (path / 'smart_buildings/evaluate.py').is_file():
            return path
    raise FileNotFoundError('Official simulator kit missing. Run tools/setup_simulator.py --source-kit <official-kit>.')


def preflight():
    modules = {'gin': 'gin-config', 'numpy': 'numpy', 'pandas': 'pandas', 'gymnasium': 'gymnasium',
               'scipy': 'scipy', 'yaml': 'PyYAML', 'numba': 'numba', 'matplotlib': 'matplotlib'}
    missing = [package for module, package in modules.items() if importlib.util.find_spec(module) is None]
    if missing:
        raise RuntimeError(f'Simulator kernel {sys.executable} lacks {", ".join(missing)}. '
                           'Run tools/setup_simulator.py and select HVAC Optimal Start Simulator in VS Code.')
