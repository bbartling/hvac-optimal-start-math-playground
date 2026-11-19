# Executed validation, 2026-11-18

The compact [summary](2026-11-18-simulation.json) was generated from the actual
completed matrix with `tools/summarize_simulation.py`. It records the source/run
signature and manifest SHA; full tick histories remain in Windows TEMP.

**60 of 60 full-length jobs passed**, each 8,640 five-minute steps: six supplied
buildings × five weather scenarios × native/adaptive policy. There were 340
AHU-scenario-policy runs, representing 170 scenario/AHU pairs and 34 physical
AHUs across six buildings. Every AHU run recorded native learning.

- 518,400 simulator steps and 2,937,600 AHU control ticks.
- Native learning: 3,395 events under native, 2,585 under adaptive.
- All jobs observed a configured maximum recirculation of 70%; this does not
  mean constant actual recirculation or validate real full-return-air recovery.
- Fixed native/adaptive samples matched. No unknown zone classifications.
  All-exterior AHUs used the documented fallback; a literal 30% count rounds up.

## What the policy comparison says

Mean raw simulator reward was -0.07869628 for native and -0.08516854 for adaptive.
Higher is better. Adaptive improved six scenarios and worsened 24. Native remains
the default. This single-seed local comparison establishes neither general
energy savings nor official leaderboard performance.

The command objectives differ: native calculates lead to the full comfort
boundary; research candidates predict arrival within 1°F, falling back to the
full-boundary native calculation when unsupported. The legacy G36 comparison
has its own documented margin. Therefore this compares two configured policies,
not the isolated effect of model selection. Common-endpoint MAE is valid for
shadow forecasts on each arm's own common cohort; it does not make the arms'
different commanded trajectories or prediction cohorts identical.

A later selector ablation should compare against a fixed predictor with the
same commanded arrival objective and plant/schedule. Do not modify the frozen
native class to force that research comparison.

## Reproduce the audit

```powershell
python tools/summarize_simulation.py --manifest "$env:TEMP\optimal-start-full-matrix-20261118\manifest.json" --out "$env:TEMP\optimal-evidence"
```

Source snapshot: `79f05d2`; package files were frozen for the run. Later notebook,
documentation and analysis-tool changes do not change the controller/estimators.
The retained input manifest SHA and run signature identify the original receipts.
The analysis refuses incomplete/unmatched jobs, unequal settings or samples,
nonfinite reward and inconsistent common-cohort counts.

Independent [trace audit](2026-11-18-trace-audit.json) verified all 60 history
hashes, all step clocks and coverage, the frozen package source, and 255,158
selector decisions reconstructed only from prior eligible errors. Zero
violations. Native updates comprise 2,238 start / 1,157 stop observations;
adaptive updates comprise 1,385 start / 1,200 stop observations. Partial response
learning is included; no minimum-change guard was added.

Separate shorter active-estimator integration runs are recorded in PROGRESS.md;
they must never be represented as full-month reward comparisons.
