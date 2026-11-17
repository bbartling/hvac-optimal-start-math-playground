"""Write a job list (scenario x start algorithm, with stop algorithms rotated)."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

HOOKED_STARTS = ["fixed_60", "fixed_120", "vavrl_static", "m0_linear_ema", "pnnl_m1_quadratic",
                 "pnnl_m2_oat_ratio", "pnnl_m3_regression", "pnnl_m4_exponential", "pnnl_median",
                 "pnnl_deployed_median_split", "repo_m5_sgd", "robust_rls", "robust_rls_zone", "v6"]
NATIVE_STARTS = ["v7", "sac_trim"]
STOPS = ["v6", "no_early_stop", "vavrl_const_drift", "linear_drift_ema", "first_order_coast"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenarios", nargs="+", required=True, help="scenario dirs")
    ap.add_argument("--starts", nargs="*", default=None)
    ap.add_argument("--stops", nargs="*", default=None)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    starts = a.starts or (HOOKED_STARTS + NATIVE_STARTS)
    stops = a.stops or STOPS
    jobs = []
    for si, sd in enumerate(a.scenarios):
        p = Path(sd)
        tag = f"{p.parent.name}__{p.name}"
        hooked = [s for s in starts if s not in NATIVE_STARTS]
        for i, st in enumerate(starts):
            stop = "native" if st in NATIVE_STARTS else stops[(hooked.index(st) + si) % len(stops)]
            jobs.append({"scenario_dir": str(p), "start": st, "stop": stop,
                         "out": str(Path(a.outdir) / tag / f"{st}__{stop}.json")})
    Path(a.out).write_text(json.dumps(jobs, indent=1))
    print(len(jobs), "jobs")


if __name__ == "__main__":
    main()
