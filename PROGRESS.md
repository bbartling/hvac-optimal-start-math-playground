# PROGRESS (overnight optimal start/stop benchmark + refactor)

Draft PR: https://github.com/bbartling/hvac-optimal-start-math-playground/pull/2 (into develop, do not merge)

## Done
- `src/hvac_optimal` package and pytest suite (55 tests pass). Old tutorials are in `archive/`; the old README is `docs/LEARN_THE_MATH.md`.
- Benchmark harness in `benchmarks/neurips_sim` (run_scenario, run_queue, make_jobs, analyze).
- Phase 1 (BensDesktop): 40 runs. Full 14 arms on b1 fairbanks_1, b1 phoenix_5 and b2 singapore_1.
- Box: Minneapolis unseen-weather runs (b1 mpls_1 complete for 8 core arms, plus b2 mpls_6 in progress).
- Added `robust_rls_fb`: robust RLS plus a Robbins-Monro feedback lead from first-hour comfort.
- Added the tolerant arrival metric (1 F, PNNL allowable deviation).
- Added warm-up logging, so lead = minutes in warm-up.

## Findings so far
- Start timing in this simulator is mostly an energy-comfort dial. All hooked algorithms lie close to the
  fixed_60 to fixed_120 trade-off line.
  - Cold climates (Fairbanks, Minneapolis Jan) are capacity-limited: AHUs run all night, and zones reach the band hours after occupancy.
  - Cooling (Phoenix, Singapore): recovery is fast. Learned models save 3-9% morning energy, at +1-7 K*min/zone first-2h unmet.
  - The simulator reward slightly prefers fixed_120 in cooling (pre-cooling mass) and later starts in cold climates.
- Stop: with guard 0.9 F (0.5 K) no algorithm ever stops early. The G36 controller holds zones only 0.4 K inside the band.
  This includes the native v6 stop, which uses the same 0.5 K guard.
  -> A dedicated stop experiment is running (fixed_120 start, guard 0.2 F, 4 stop arms x 4 b1 scenarios).

## Running (detached)
- Desktop: phase2 queue `%TEMP%\osbench\phase2_jobs.json`, log `phase2_jobs.log`, results `%TEMP%\osbench\results\phase1`.
  116 jobs, about 15/h, ETA about 04:30.
- Box: `/workspace/osbench/box_chain.sh` runs `stopexp_jobs.json` (16 runs: fixed_120 start x {no_early_stop, first_order_coast, vavrl_const_drift, v6} x b1 {denver_7, atlanta_2, minneapolis_1, phoenix_5}, guard 0.2 F; log stopexp.log; it only progresses while a box shell is active, so keep `sleep 290` polls running), then `boxmpls2_jobs.json`.

- Desktop chain3.ps1 (after phase 2): phase3_jobs.json = fixed_60 anchors on the 6 reduced scenarios plus fixed_180 on all 12
  phase-1 scenarios (the schedule-curve anchors for the "savings beyond schedule" criterion in analyze.py).

- The box reboots now and then, which kills its jobs. After a resume, check `pgrep -fa run_queue` and relaunch
  `setsid nohup /workspace/osbench/box_chain.sh > /workspace/osbench/box_chain.out 2>&1 < /dev/null &`.
  It is resumable. Box files persist.

## Next
1. When the runs finish, copy the results to the box and run
   `analyze.py results/phase1 results/boxmpls --out an_all` and `analyze.py results/stopexp --out an_stop --all-days`.
2. Pick the winners: frontier vs fixed schedules, simulator reward, and minimax regret across scenarios.
   Set RECOMMENDED_* and README tables.
3. Final README, update the PR body, mark it ready (do not merge).


## 2026-11-16 22:50 CST: interim results in the README
- README now has the plain-English findings and the interim tables. Regenerate them with
  `python benchmarks/neurips_sim/update_readme.py <an_all> --stop <an_stop> --note "..."`.
- Interim: no start algorithm beats the fixed-schedule frontier consistently. m0_linear_ema
  and v6 come out about even. Stop: first_order_coast with a 0.2 F guard saves about 8 % of
  end-of-day energy (Denver 7 only so far).
- Still running: desktop phase2 (Denver 8 onward) then phase3 (fixed anchors), and box
  stopexp then boxmpls2.
