# Local rewrite checkpoint — 2026-11-18

Branch: `rewrite/java-reference-tutorial`. Canonical work stays in this checkout.
No push, Kaggle upload/submission or field write has been performed.

## Current verified state after quota renewal

November 19 simulator migration COMPLETE: this checkout now owns `.kit` and
`.venv-sim`, both ignored by Git. The existing official kit was imported read-only
with a file-hash manifest; the sibling checkout and its environment were not
modified. `tools/setup_simulator.py` provisions dependencies from the committed
lock file and registers **HVAC Optimal Start Simulator**. Local notebook kit
discovery uses this repository; no sibling path is needed. Missing kernel
dependencies fail before worker startup, and failed jobs raise a notebook error.

Validation: **155 tests passed**, `pip check` passed, and the actual notebook
executed using the new environment with **30/30 scenarios passing at 12 steps**,
zero failures (163 seconds). This is migration/integration validation, not a new
full-month score comparison. Evidence is under
`%TEMP%\optimal-self-contained-notebook-20261119` and
`%TEMP%\optimal-start-stop-runs-5dz_7603`.

The local notebook is enabled for full 8,640-step runs with the registered kernel.
Reload it from disk, select that kernel, restart, then Run All. Exported Kaggle
bundles retain the generic Python kernel and disable the optional simulator so
the lightweight offline tutorial still works without a separately attached kit.
The user's earlier notebook with all 30 missing-gin failures was retained only
as a TEMP diagnostic before regeneration. No earlier failures are presented as
successful simulations.

Follow-up, November 19: added **Controller without NumPy or pandas** to the
notebook. It explains primitive arithmetic, vanilla-Java portability, the native
MPD versus rate-EMA distinction, and fixed/irregular sampling for M4. The plain
Python 3.10+ example uses the existing complete native driver and prints an
eligible partial-response update without importing numerical/plotting packages.
The extracted notebook cell passed in a fresh `python -S` subprocess importing
the bundled ZIP; third-party numerical modules were absent. Four targeted tests
passed, plus fresh-kernel execution of the full notebook. Core code is unchanged.
The notebook now has 22 cells, nine code cells. Latest preview and bundle:
`%TEMP%\optimal-stdlib-notebook-preview-20261119` and
`%TEMP%\optimal-stdlib-kaggle-bundle-20261119`.

Renewed at 2026-11-19 01:20:50 UTC; resumed after the requested quota sleep.
**60/60 full 30-day simulator jobs passed, zero failures.** Six buildings,
five weather cities, 30 scenarios, 34 physical AHUs, 340 AHU-scenario-policy runs.
All 340 AHU instances learned; 5,980 total native updates. Full independent audit
checked all 2,937,600 AHU ticks, all 60 history hashes and 255,158 causal selector
decisions: zero violations. Package sources matched snapshot `79f05d2` throughout
those runs. The later Windows persistence fix changes only result publication;
native/controller/estimator/sampling calculations remain unchanged.

Native reward exceeded adaptive on 24/30 scenarios. Commanded arrival objectives
differ (full boundary native, 1°F research with native fallback), so this is not
an isolated selector ablation. Native remains default. See docs/validation/.

At the full simulator checkpoint: **151 tests passed**. Its 20-cell, 8-code-cell source notebook was 22,511
bytes. Fresh-kernel offline execution passed from both ZIP and unpacked driver
bundles, with HTTP disabled. A wheel was built in TEMP and installed without
dependencies into a clean TEMP environment; core imports and CLI passed.

Current artifacts under `%TEMP%`:

- `optimal-final-kaggle-bundle-20261118`: final offline notebook/driver/data.
- `optimal-final-notebook-preview-20261118/tutorial_preview.html`: executed preview.
- `optimal-final-evidence-20261118`: aggregate JSON/CSV and actual AHU trace PNGs.
- `optimal-final-wheel-20261118`: wheel; `optimal-driver-venv-20261118`: clean install.

Completed: **240/240 active-estimator integration jobs** (eight research policies
× all 30 scenarios), 360 steps each, phase start, four workers, 1,360 AHU runs.
Every job called its predictor. All 240 histories passed SHA checks. There were
769 native updates; 591 AHU runs had no eligible update within the short horizon.
These are control-path integration tests, not full-month score comparisons.

Three transient Windows manifest replacements created synthetic failed duplicate
rows while durable jobs were complete. Identical-source resume reconciled 240
valid receipts, zero failures, without new simulation attempts (240 total).
The IO-only fix adds bounded PermissionError retry/temp cleanup and separates
publication failure from worker outcomes. A new real two-job, 12-step smoke
forced WinError 5 using an actual Windows reader: retry and no-rerun resume
passed. Evidence: `%TEMP%\optimal-fixed-publication-smoke-jwa1zhb8`.

All simulator jobs are finished. No further broad run is required for the
persistence-only fix. The old matrix outputs retain their frozen source identity;
use a new TEMP output directory to run the current package, whose source hash
now includes that IO change. Existing result audits remain valid.

## Implemented

- Source-traceable Java behavior port for BOTH start and stop, four independent
  minutes/degree learners, and documented framework assumptions. No added native
  learning gates. Owner Java is not distributed.
- Standard-library estimator, causal replay, AHU zone sampling, IoT JSONL,
  dataset inventory, offline bundle and official simulator drivers.
- Default 30% fixed per-AHU sample, exterior/interior balance where metadata
  permits, equal weights unless configured. Full-recirculation BAS note and
  observed simulator 70% cap are explicit.
- Slim 20-cell notebook, with model provenance, recorded-data comparisons,
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

## Historical full-matrix launch / reproduction

Terminal observation handling is fixed and regression tested, with no extra
native tick, learning update or plant action. Package source is now FROZEN while
the actual simulator runs; do not edit any `hvac_optimal/*.py` during the matrix.

Completed: 60 full-length jobs (all 30 scenarios × native and research-winner),
8,640 five-minute steps each, phase both, four workers, seed 0, sample 30%.
All eight research models are shadow-assessed independently per AHU in each job;
this is not eight separately controlled energy experiments.

- Output: `%TEMP%\optimal-start-full-matrix-20261118\manifest.json`.
- Log: `%TEMP%\optimal-start-full-matrix-20261118.log`.
- Shell session ID at launch: 96494 (may expire; process/manifest are authoritative).
- Simulator Python: sibling `.venv-sim\Scripts\python.exe`; official kit `.kit`.
- At launch there were no completed jobs; all 60 have since passed and been audited.

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

Full-run coverage, learning, cohort and integrity checks are now complete.
Keep official leaderboard claims separate from local raw reward.

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
