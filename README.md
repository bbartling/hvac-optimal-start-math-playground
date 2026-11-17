# HVAC optimal start & stop: PNNL's four models vs. the G36 recovery learner vs. a two-number EMA

One self-contained, Kaggle-ready tutorial notebook,
[`optimal_start_stop_tutorial.ipynb`](optimal_start_stop_tutorial.ipynb). In plain language it explains, implements and
benchmarks:

* the **four optimal-start models** from PNNL's field study (Kim, Yu, Lutes & Katipamula, *Applied Thermal Engineering*
  257 (2024) 124256, [doi](https://doi.org/10.1016/j.applthermaleng.2024.124256), PDF in [`PNNL_Paper/`](PNNL_Paper/)),
  plus PNNL's deployed **median-of-four** ensemble,
* the **G36 recovery learner (v7)** start rule from our NeurIPS 2026 Smart Buildings controller,
* a **linear-rate EMA**, the simplest learner (two stored numbers),
* **optimal stop** with a first-order (1R1C) coast-down model,

all run closed-loop in Google's Smart Buildings simulator (the NeurIPS 2026 Smart Buildings challenge): 6 office
buildings, 6 climates, 22 thirty-day scenarios. Fixed 60/120/180-min starts are shown as the baseline.

Each algorithm gets the same layout: **How it works**, **Code**, **Evaluation** (offline replay of recorded recoveries
plus closed-loop results by climate). The notebook ends with a **deployability / complexity** ranking (Big-O, memory,
measured micro-benchmarks) and a **"best pick when you only have a standard math library"** section with stdlib-only
Python, JavaScript and Lua code.

## Run it

```bash
pip install -r requirements.txt
jupyter lab optimal_start_stop_tutorial.ipynb
```

It needs only numpy, pandas and matplotlib (jinja2 for the styled tables), and runs top to bottom in under a minute. The
small result files (about 0.4 MB) are in [`data/`](data/).

**Kaggle:** upload the files in `data/` as a dataset, attach it to the notebook, and run. The notebook finds the files in
`../input/<dataset>/` automatically. If no local copy is found, it downloads the same files from this repo.

## Results

### Winners


There is **no single winner**; it depends what you measure.

| what you care about | winner | runner-up |
|---|---|---|
| 🏆 **Competition score** (the official whole-month score) | **G36 recovery learner (v7)**: +0.74 % vs a fixed 2 h start, worst scenario +2.5 % | PNNL median of four (+0.88 %, worst +4.9 %) |
| Energy saved at equal comfort | **PNNL median of four** (+1.76 %) | **Linear-rate EMA** (+1.60 %) |
| Comfort (fewest late mornings) | **PNNL median of four** (40 %) | Linear-rate EMA (43 %); v7 47 % |
| Predicting warm-up time | **Linear-rate EMA** (29 min average error) | PNNL Model 4 (36 min) |
| Fewest late *starts* in the replay | **v7 rule** (16 %, thanks to its ×1.25 + 15 min margin) | PNNL Model 1 (23 %) |
| Simplest to deploy (no libraries) | **Linear-rate EMA** (2 numbers, ~9 lines) | v7 start rule (2 numbers, ~14 lines) |
| Evening optimal stop | **First-order coast-down**: +3.0 % evening energy for +0.7 °F·min/zone | — |

* **Plain truth:** none of the learners beats a plain fixed 2-hour start on the competition score in this simulator; the
  differences are under 1 %. Start time here is mostly an energy-vs-comfort dial.
* **Pick v7** for the competition. **Pick the EMA** for a real controller with only basic math. **Pick the PNNL median**
  if you can run four models and care most about comfort.

### Start leaderboard (all 22 scenarios unless noted)

* **Competition score:** the official NeurIPS score for the 30-day run (energy + carbon + comfort), shown as % worse than a
  fixed 120-min start. Lower is better.
* **Savings beyond schedule:** extra morning energy saved compared with a fixed schedule that gives the same comfort.
  Higher is better.

| start algorithm | scenarios | competition score % (mean) | … worst | savings beyond schedule % | … worst | late % (1 °F tol.) | energy saved vs fixed 120 % |
|---|---|---|---|---|---|---|---|
| **G36 recovery learner (v7)** | 22 | **+0.74** | **+2.54** | -0.83 | -6.04 | 46.9 | 4.2 |
| PNNL median of M1-M4 | 22 | +0.88 | +4.85 | **+1.76** | **-0.61** | **40.0** | 3.7 |
| Linear-rate EMA | 22 | +0.96 | +4.90 | +1.60 | -0.78 | 42.6 | 8.5 |
| PNNL M4 · exponential | 22 | +1.93 | +5.85 | -0.40 | -9.48 | 45.1 | 13.8 |
| PNNL M3 · regression | 6 | +0.54 | +1.53 | +0.33 | -1.31 | 45.9 | 0.1 |
| PNNL M1 · quadratic | 6 | +0.61 | +1.41 | +0.29 | -1.09 | 47.3 | -0.1 |
| PNNL M2 · OAT ratio | 6 | +0.88 | +1.66 | +0.49 | -0.58 | 47.8 | 3.6 |
| Fixed 120 min (baseline) | 22 | 0.00 | 0.00 | 0.00 | 0.00 | 33.9 | 0.0 |

PNNL M1-M3 were only run on 6 scenarios, so compare them with the head-to-head table in the notebook (on those same 6
scenarios v7 scores +0.79 %, the median +0.72 % and the EMA +1.32 %). No learner beats a plain fixed 2-hour start on the
competition score in this simulator; the gaps are under 1 %.

### Offline replay: predicted vs actual warm-up time (1,033 recorded recoveries)

| model | MAE (min) | bias (min) | late starts % | within ±15 min % |
|---|---|---|---|---|
| **Linear-rate EMA** | **28.9** | -14.1 | 25.8 | 62.1 |
| PNNL M4 · exponential | 35.8 | -22.6 | 58.4 | **69.3** |
| PNNL M2 · OAT ratio | 36.2 | +0.3 | 26.1 | 61.5 |
| PNNL median of M1-M4 | 36.3 | +3.6 | 25.0 | 58.0 |
| PNNL M1 · quadratic | 38.9 | +10.8 | 23.2 | 54.5 |
| PNNL M3 · regression | 39.1 | +12.8 | 26.9 | 51.5 |
| G36 recovery learner (v7) | 44.5 | +19.4 | **15.8** | 40.9 |

v7 deliberately starts early (×1.25 + 15 min margin), so its average error is larger but it has the fewest late starts.

### Deployability (simplest first)

| rank | algorithm | per-day update | memory | lines of code | predict (µs) | update (µs) | saved state (bytes) |
|---|---|---|---|---|---|---|---|
| 1 | Linear-rate EMA | O(1) | O(1): 2 numbers | 9 | 0.1 | 0.3 | 84 |
| 2 | PNNL M1 · quadratic | O(T) | O(W) | 24 | 3.6 | 1.8 | 458 |
| 3 | PNNL M4 · exponential | O(T) | O(W) | 22 | 3.6 | 20.7 | 151 |
| 4 | G36 recovery learner (v7) | O(T) | O(1): 2 numbers | 14 | 2.1 | 5.2 | 229 |
| 5 | PNNL M2 · OAT ratio | O(1) | O(W) | 21 | 5.1 | 0.6 | 217 |
| 6 | PNNL M3 · regression | O(T) | O(W) | 33 | 3.6 | 2.2 | 530 |
| 7 | PNNL median of M1-M4 | O(T) | O(W), ~7·W numbers | 90 | 17.3 | 32.4 | 1,196 |

T = warm-up samples in one morning, W = PNNL's 8-day history window. Micro-benchmarks are single-core Python on the build
machine; all of these are trivially cheap for any controller. None needs numpy: PNNL M4's least squares is one variable
(two running sums).

**Best pick with only a standard math library: the linear-rate EMA.** Only `+ - * / max`, two stored numbers, the best
predictor and nearly the best energy at equal comfort. You give up ~0.2 percentage points of competition score vs. v7.

### Optimal stop (fixed 120-min start, 0.2 °F guard, one building in Atlanta, Denver, Minneapolis and Phoenix)

| stop algorithm | days stopped early % | restarts/day | unmet last 3 h °F·min/zone | evening energy saved % | reward gain |
|---|---|---|---|---|---|
| **First-order coast** | 5.7 | 0.43 | 12.56 | 3.01 | -0.009 |
| Constant drift 0.35 °F/h | 2.1 | 0.69 | 17.58 | 5.71 | -0.050 |
| G36 stop (v6/v7 controller) | 0.6 | 0.00 | 11.68 | -0.05 | +0.004 |
| No early stop | 0.0 | 0.00 | 11.82 | 0.00 | +0.000 |

With the default 0.9 °F guard, the stop algorithms almost never fired (under 0.4 % of AHU-days), because the G36 sequence
holds zones close to the band edge in the late afternoon.

## Repository layout

| path | what |
|---|---|
| `optimal_start_stop_tutorial.ipynb` | the tutorial, executed, with all outputs |
| `data/` | small result files the notebook loads (scored mornings, stop experiment, recorded recoveries) |
| `PNNL_Paper/` | the PNNL paper the notebook implements |
| `requirements.txt` | numpy, pandas, matplotlib, jinja2, jupyter |

## Where the old lessons and code went

This repo used to hold a set of optimal-start lessons, the `hvac_optimal` Python package, tests, and the closed-loop benchmark
harness (job runner, simulator hooks, `analyze.py`) that produced the data here. All of it is preserved, unchanged, at:

* tag [`archive/pre-strip-2026-11-17`](https://github.com/bbartling/hvac-optimal-start-math-playground/tree/archive/pre-strip-2026-11-17)
* branch [`archive/pre-strip`](https://github.com/bbartling/hvac-optimal-start-math-playground/tree/archive/pre-strip)

## License

See [LICENSE](LICENSE).
