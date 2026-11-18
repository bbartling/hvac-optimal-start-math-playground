# Local rewrite checkpoint — 2026-11-18

Branch: `rewrite/java-reference-tutorial`. Canonical work stays in this checkout.
No push, Kaggle upload/submission or field write has been performed.

## Implemented

- Source-traceable Java behavior port for BOTH start and stop, four independent
  minutes/degree learners, and documented framework assumptions. No added native
  learning gates. Owner Java is not distributed.
- Standard-library estimator, causal replay, AHU zone sampling, IoT JSONL,
  dataset inventory, offline bundle and official simulator drivers.
- Default 30% fixed per-AHU sample, exterior/interior balance where metadata
  permits, equal weights unless configured. Full-recirculation BAS note and
  observed simulator 70% cap are explicit.
- Slim 19-cell notebook, with model provenance, recorded-data comparisons,
  learning/selection charts, optional actual-simulator traces and an IoT example.

## Verified before the broad simulator matrix

- 138 tests passed, including 327 compiled-Java differential ticks using the
  supplied source with documented time/status SDK stubs. This is not Niagara
  runtime certification.
- All 1,163 recorded recovery events retained; eight predictors, 9,304 records.
  Partial/censored observations stay visible and predictions precede training.
- Fresh-kernel notebook passed. Exported notebook also passed from TEMP using
  only the bundled driver ZIP and data, with Python HTTP requests disabled.
- Actual official simulator bootstrap passed (12 steps, four independent AHUs).
  This proves integration only, not multi-building or full-month performance.

TEMP evidence: `optimal-final-preview-20261118-v2`,
`optimal-final-offline-preview-20261118-v3`,
`optimal-final-bundle-20261118-v3` under `%TEMP%`.

## Next / resume

Terminal observation handling is fixed and regression tested, with no extra
native tick, learning update or plant action. Package source is now FROZEN while
the actual simulator runs; do not edit any `hvac_optimal/*.py` during the matrix.

Running: 60 full-length jobs (all 30 scenarios × native and research-winner),
8,640 five-minute steps each, phase both, four workers, seed 0, sample 30%.
All eight research models are shadow-assessed independently per AHU in each job;
this is not eight separately controlled energy experiments.

- Output: `%TEMP%\optimal-start-full-matrix-20261118\manifest.json`.
- Log: `%TEMP%\optimal-start-full-matrix-20261118.log`.
- Shell session ID at launch: 96494 (may expire; process/manifest are authoritative).
- Simulator Python: sibling `.venv-sim\Scripts\python.exe`; official kit `.kit`.
- No completed full-length jobs at launch. Do not report them as passed yet.

Resume by inspecting manifest/log and process status first. Run the same command
only if no matrix process remains; matching source/config and complete history
SHA are required for resume. Command from canonical project root:

```powershell
$env:SMART_BUILDINGS_KIT = 'C:\Users\ben\Documents\neurips-2026-smart-buildings\.kit'
$env:PYTHONPATH = "$PWD;$env:SMART_BUILDINGS_KIT"
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTHONPYCACHEPREFIX = "$env:TEMP\optimal-matrix-cache-20261118"
$env:NUMBA_CACHE_DIR = "$env:TEMP\optimal-matrix-numba-20261118"
$env:MPLCONFIGDIR = "$env:TEMP\optimal-matrix-mpl-20261118"
$env:OMP_NUM_THREADS = '1'
$env:OPENBLAS_NUM_THREADS = '1'
$env:MKL_NUM_THREADS = '1'
& 'C:\Users\ben\Documents\neurips-2026-smart-buildings\.venv-sim\Scripts\python.exe' -m hvac_optimal simulate --kit "$env:SMART_BUILDINGS_KIT" --out "$env:TEMP\optimal-start-full-matrix-20261118" --policies native winner --steps 8640 --workers 4 --phase both
```

After completion: inspect failures, learning counts, all-six-building AHU
coverage, common-cohort error, actual recirculation caps and local reward scope.
Plot representative real traces; record measured evidence in this file/docs and
commit locally. Keep official leaderboard claims separate from local raw reward.

Quota policy: inspect actual account limits at milestones. At 10% or less
five-hour remaining, commit coherent work, record running jobs and reset time,
sleep until renewal, then continue. Do not consume a reset credit automatically.

### Quota sleep checkpoint

2026-11-18 20:49 UTC (14:49 Central): actual five-hour usage reached 90% used,
10% remaining. Account reports renewal at **2026-11-19 01:20:50 UTC**
(November 18, 19:20:50 Central). Weekly remaining was 42%.
Source checkpoint commit: `79f05d2`. Working tree was clean after that commit.
Matrix process and four workers were alive; manifest reported 60 jobs,
0 completed, 0 failed at launch. Let them continue during quota sleep.
Next action after renewal: inspect actual account usage, matrix manifest,
worker processes and error log; then resume validation. No reset credit used.
