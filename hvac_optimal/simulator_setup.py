"""Standard-library-only discovery and diagnostics for optional simulator use."""
import importlib.util
from pathlib import Path
import sys
import json
import os
import subprocess


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


def run_notebook_matrix(kit, out, *, policies=('native',), steps=360, workers=1, limit=1):
    """Use the project environment even when VS Code selected another kernel."""
    root = Path(__file__).resolve().parents[1]
    local = root / '.venv-sim' / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
    python = str(local) if local.is_file() else sys.executable
    out = Path(out)
    log = out.with_name(out.name + '.log')
    command = [python, '-m', 'hvac_optimal', 'simulate', '--kit', str(kit), '--out', str(out),
               '--policies', *policies, '--steps', str(steps), '--workers', str(workers)]
    if limit is not None:
        command += ['--limit', str(limit)]
    environment = os.environ.copy()
    environment['PYTHONPATH'] = os.pathsep.join([str(root), str(kit), environment.get('PYTHONPATH', '')])
    print(f'Running {limit or "all"} scenario(s), {steps} steps, using {python}', flush=True)
    print(f'Results: {out}', flush=True)
    with log.open('w', encoding='utf-8') as stream:
        result = subprocess.run(command, env=environment, stdout=stream, stderr=subprocess.STDOUT)
    if result.returncode:
        raise RuntimeError(f'Simulator failed. Log: {log}\n{log.read_text(encoding="utf-8")[-4000:]}')
    receipt = json.loads((out / 'manifest.json').read_text(encoding='utf-8'))
    if receipt['failed']:
        raise RuntimeError(f'Simulator jobs failed. See {log}')
    return receipt
