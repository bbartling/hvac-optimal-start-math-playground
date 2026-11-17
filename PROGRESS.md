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
  -> A dedicated stop experiment is running (fixed_120 start, guard 0.2 F, 6 stop arms x 6 b1 scenarios).

## Running (detached)
- Desktop: phase2 queue `%TEMP%\osbench\phase2_jobs.json`, log `phase2_jobs.log`, results `%TEMP%\osbench\results\phase1`.
  116 jobs, about 15/h, ETA about 04:30.
- Box: `/workspace/osbench/box_chain.sh` runs `stopexp_jobs.json` (36 runs, log stopexp.log), then `boxmpls2_jobs.json`.

- Desktop chain3.ps1 (after phase 2): phase3_jobs.json = fixed_60 anchors on the 6 reduced scenarios plus fixed_180 on all 12
  phase-1 scenarios (the schedule-curve anchors for the "savings beyond schedule" criterion in analyze.py).

## Next
1. When the runs finish, copy the results to the box and run
   `analyze.py results/phase1 results/boxmpls --out an_all` and `analyze.py results/stopexp --out an_stop --all-days`.
2. Pick the winners: frontier vs fixed schedules, simulator reward, and minimax regret across scenarios.
   Set RECOMMENDED_* and README tables.
3. Final README, update the PR body, mark it ready (do not merge).
