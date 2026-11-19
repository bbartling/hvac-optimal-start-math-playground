"""Execute the source notebook without overwriting it; save a TEMP preview."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import time

import nbformat
from nbclient import NotebookClient


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--bundle", type=Path, help="validate exported offline assets from outside the checkout")
    parser.add_argument("--unpacked", action="store_true", help="assert local unpacked driver import instead of ZIP")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    working = args.bundle.resolve() if args.bundle else root
    source = working / "optimal_start_stop_tutorial.ipynb"
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    for variable, directory in [("MPLCONFIGDIR", "mpl"), ("IPYTHONDIR", "ipython"),
                                ("JUPYTER_RUNTIME_DIR", "jupyter")]:
        (out / directory).mkdir(exist_ok=True)
        os.environ[variable] = str(out / directory)
    before = hashlib.sha256(source.read_bytes()).hexdigest()
    notebook = nbformat.read(source, as_version=4)
    if args.bundle:
        # Kernel transport stays available, while tutorial HTTP access fails.
        notebook.cells.insert(0, nbformat.v4.new_code_cell(
            "import urllib.request, http.client\n"
            "def offline_only(*args, **kwargs):\n"
            "    raise AssertionError('Network access is disabled for bundle validation')\n"
            "urllib.request.urlopen = offline_only\n"
            "http.client.HTTPConnection.connect = offline_only\n"
            "http.client.HTTPSConnection.connect = offline_only\n"))
        origin_check = ("assert Path(hvac_optimal.__file__).resolve().is_relative_to(Path.cwd()), hvac_optimal.__file__"
                        if args.unpacked else "assert 'hvac_optimal_driver.zip' in hvac_optimal.__file__, hvac_optimal.__file__")
        notebook.cells.append(nbformat.v4.new_code_cell(
            "import hvac_optimal\n" + origin_check + "\n"
            "print('Verified offline driver origin:', hvac_optimal.__file__)"))
        os.environ.pop("PYTHONPATH", None)
    start = time.monotonic()
    try:
        NotebookClient(notebook, timeout=180, kernel_name="python3",
                       resources={"metadata": {"path": str(working)}}).execute()
    finally:
        nbformat.write(notebook, out / "executed_tutorial.ipynb")
    assert hashlib.sha256(source.read_bytes()).hexdigest() == before
    images = []
    for index, cell in enumerate(notebook.cells):
        for output_index, output in enumerate(cell.get("outputs", [])):
            png = output.get("data", {}).get("image/png")
            if png:
                target = out / f"figure-cell-{index}-{output_index}.png"
                target.write_bytes(base64.b64decode(png))
                images.append(str(target))
    try:
        from nbconvert import HTMLExporter
        body, _ = HTMLExporter().from_notebook_node(notebook)
        (out / "tutorial_preview.html").write_text(body, encoding="utf-8")
    except ImportError:
        pass
    receipt = {"status": "PASS", "source_sha256": before, "source_bytes": source.stat().st_size,
               "offline_bundle": bool(args.bundle), "working_directory": str(working),
               "code_cells": sum(c.cell_type == "code" for c in notebook.cells),
               "seconds": round(time.monotonic() - start, 2), "images": images}
    (out / "validation.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt))


if __name__ == "__main__":
    main()
