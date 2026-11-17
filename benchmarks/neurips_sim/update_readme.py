"""Copy the key tables from an analyze.py output into README.md (between markers).

    python update_readme.py <analysis dir> [--stop <stop analysis dir>] [--note "text"]
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
START, END = "<!-- RESULTS:START -->", "<!-- RESULTS:END -->"


def section(md: str, title: str) -> str:
    m = re.search(r"^## " + re.escape(title) + r".*?$(.*?)(?=^## |\Z)", md, re.S | re.M)
    return m.group(1).strip() if m else "(not available yet)"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("analysis")
    ap.add_argument("--stop", default=None)
    ap.add_argument("--note", default="")
    a = ap.parse_args()
    md = (Path(a.analysis) / "summary.md").read_text()
    head = md.split("\n## ")[0].replace("# Benchmark summary", "").strip()
    parts = [START, "", a.note, "", f"**Coverage:** {head}", "",
             "### Start: evidence used to pick the winner", "", section(md, "Winner criteria (start)"), "",
             "### Start: mean over scenarios (each scenario weighted equally)", "",
             section(md, "Start, mean over scenarios"), "",
             "### Start by climate", "", section(md, "Compact: start by climate"), "",
             "### Start by season", "", section(md, "Compact: start by season"), "",
             "### Start on post-weekend / post-holiday days (Monday problem)", "",
             section(md, "Optimal start by post_weekend"), ""]
    if a.stop:
        smd = (Path(a.stop) / "summary.md").read_text()
        parts += ["### Stop (dedicated experiment: same fixed_120 start, stop guard 0.2 F)", "",
                  section(smd, "Optimal stop (runs with the hooked G36 plant)"), "",
                  section(smd, "Optimal stop by city"), ""]
    parts += [END]
    readme = ROOT / "README.md"
    txt = readme.read_text()
    block = "\n".join(parts)
    if START in txt:
        txt = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda _: block, txt, flags=re.S)
    else:
        txt = txt.rstrip() + "\n\n## Results\n\n" + block + "\n"
    readme.write_text(txt)
    print("README updated")


if __name__ == "__main__":
    main()
