"""Provision this checkout's official kit and independent Python environment."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import venv

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-kit', type=Path, help='Existing official kit directory (read-only migration source)')
    args = parser.parse_args()
    kit = ROOT / '.kit'
    if args.source_kit:
        source = args.source_kit.resolve() / 'smart_buildings'
        target = kit / 'smart_buildings'
        if not (source / 'evaluate.py').is_file():
            parser.error('source kit must contain smart_buildings/evaluate.py')
        if target.exists():
            parser.error('local kit already exists; refusing to overwrite it')
        shutil.copytree(source, target, ignore=shutil.ignore_patterns('__pycache__', '*.pyc', 'results'))
        hashes = {p.relative_to(kit).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in target.rglob('*') if p.is_file()}
        (kit / 'source-manifest.json').write_text(json.dumps({'sha256': hashes}, indent=2), encoding='utf-8')
    if not (kit / 'smart_buildings/evaluate.py').is_file():
        parser.error('Supply --source-kit with a legitimately obtained official competition kit')
    environment = ROOT / '.venv-sim'
    if not environment.exists():
        venv.EnvBuilder(with_pip=True).create(environment)
    python = environment / ('Scripts/python.exe' if sys.platform == 'win32' else 'bin/python')
    requirements = ROOT / 'requirements-simulator-lock.txt'
    if not requirements.exists():
        requirements = ROOT / 'requirements-simulator.txt'
    subprocess.run([str(python), '-m', 'pip', 'install', '-r', str(requirements)], check=True)
    subprocess.run([str(python), '-m', 'ipykernel', 'install', '--user', '--name', 'hvac-optimal-sim',
                    '--display-name', 'HVAC Optimal Start Simulator'], check=True)
    print('Ready. Select the HVAC Optimal Start Simulator kernel in VS Code.')


if __name__ == '__main__':
    main()
