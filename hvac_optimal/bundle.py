"""Create a versioned, offline Kaggle dataset bundle using only stdlib."""

from pathlib import Path
import hashlib
import json
import shutil
import zipfile


def build_bundle(project_root, output_dir):
    root, out = Path(project_root).resolve(), Path(output_dir).resolve()
    if out == root or root in out.parents and not out.name.startswith(("kaggle", "dist")):
        raise ValueError("choose a dedicated bundle output directory or Windows TEMP")
    out.mkdir(parents=True, exist_ok=True)
    archive = out / "hvac_optimal_driver.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for path in sorted((root / "hvac_optimal").glob("*.py")):
            bundle.write(path, "hvac_optimal/" + path.name)
        for path in sorted((root / "LICENSES").glob("*")):
            if path.is_file():
                bundle.write(path, "LICENSES/" + path.name)
        for name in ("LICENSE", "AGENTS.md"):
            if (root / name).is_file():
                bundle.write(root / name, name)
    (out / "data").mkdir(exist_ok=True)
    # Only observed recoveries/trajectories are needed for the corrected
    # tutorial. Old confounded monthly scores are deliberately not packaged.
    for name in ("recovery_events.csv.gz", "recovery_traces.csv.gz", "recovery_manifest.json"):
        shutil.copyfile(root / "data" / name, out / "data" / name)
    notebook = root / "optimal_start_stop_tutorial.ipynb"
    shutil.copyfile(notebook, out / notebook.name)
    assets = [archive, out / notebook.name, *sorted((out / "data").glob("*"))]
    manifest = {
        "format_version": 1, "purpose": "offline educational notebook; not a competition policy submission",
        "source_package_version": "0.1.0", "simulator_included": False,
        "simulator_note": "Attach the official competition dataset separately to run its simulator.",
        "assets": {str(p.relative_to(out)).replace("\\", "/"): hashlib.sha256(p.read_bytes()).hexdigest() for p in assets},
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest
