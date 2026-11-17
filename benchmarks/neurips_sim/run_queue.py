"""Run a benchmark job list with N parallel simulator workers (resumable).

jobs file: JSON list of {"scenario_dir", "start", "stop", "out"}; finished jobs
(``out`` json exists) are skipped, so the queue can be restarted at any time.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", required=True)
    ap.add_argument("--neurips-root", required=True)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--steps", type=int, default=8640)
    ap.add_argument("--actor", default=None)
    ap.add_argument("--log", default=None)
    a = ap.parse_args()
    jobs = json.loads(Path(a.jobs).read_text())
    log = open(a.log or (Path(a.jobs).with_suffix(".log")), "a", buffering=1)

    def say(msg):
        log.write(time.strftime("%H:%M:%S ") + msg + "\n")

    pending = [j for j in jobs if not Path(j["out"]).exists()]
    say(f"queue start: {len(pending)} of {len(jobs)} jobs pending, workers={a.workers}")
    running = []
    t0 = time.time()
    done = 0
    while pending or running:
        while pending and len(running) < a.workers:
            if (HERE / "STOP").exists():
                pending = []
                break
            j = pending.pop(0)
            Path(j["out"]).parent.mkdir(parents=True, exist_ok=True)
            cmd = [sys.executable, str(HERE / "run_scenario.py"), "--neurips-root", a.neurips_root,
                   "--scenario-dir", j["scenario_dir"], "--start", j["start"], "--stop", j["stop"],
                   "--steps", str(a.steps), "--out", j["out"]]
            cmd += [str(x) for x in j.get("args", [])]
            if j["start"] == "sac_trim" and a.actor:
                cmd += ["--actor", a.actor]
            errf = open(str(j["out"]).replace(".json", ".err"), "w")
            env = dict(os.environ)
            for k in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "NUMBA_NUM_THREADS"):
                env.setdefault(k, "1")  # one core per simulator; avoid oversubscription
            p = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=errf, env=env)
            running.append((p, j, time.time(), errf))
        time.sleep(2)
        still = []
        for p, j, ts, errf in running:
            rc = p.poll()
            if rc is None:
                still.append((p, j, ts, errf))
                continue
            errf.close()
            done += 1
            say(f"{'OK ' if rc == 0 else 'ERR'} rc={rc} {Path(j['scenario_dir']).parent.name}/{Path(j['scenario_dir']).name} "
                f"start={j['start']} stop={j['stop']} {(time.time() - ts) / 60:.1f} min "
                f"[{done} done, {len(pending)} pending, {(time.time() - t0) / 3600:.2f} h]")
        running = still
    say("queue finished")


if __name__ == "__main__":
    main()
