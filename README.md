# HVAC optimal start & stop: the four PNNL models vs. a one-line learner

One self-contained, Kaggle-ready tutorial notebook,
[`optimal_start_stop_tutorial.ipynb`](optimal_start_stop_tutorial.ipynb). It explains, implements and benchmarks:

* the **four optimal-start models** from PNNL's field study (Kim, Yu, Lutes & Katipamula, *Applied Thermal Engineering*
  257 (2024) 124256, [doi](https://doi.org/10.1016/j.applthermaleng.2024.124256), PDF in [`PNNL_Paper/`](PNNL_Paper/)),
  plus PNNL's deployed median-of-four ensemble,
* the best algorithm from this repo's earlier work, a **linear-rate EMA**,
* **optimal stop** with a first-order (1R1C) coast-down model,

all run closed-loop in Google's Smart Buildings simulator (the NeurIPS 2026 Smart Buildings challenge): 6 office
buildings, 6 climates, 22 thirty-day scenarios, 252 simulations, 23,136 scored air-handler mornings.

Each algorithm gets the same section layout: **How it works** (intuition, equation, inputs, fitting, worked example),
**Code** (a compact implementation), **Evaluation** (offline replay of recorded recoveries plus closed-loop results by climate).

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
* **Optimal start: linear-rate EMA**, $\widehat{t} = \Delta T / R$ with $R \leftarrow R + 0.2\,(\Delta T_0/t_{act} - R)$.
  Of the algorithms run on all 22 scenarios, it is the only one with positive mean savings beyond a fixed schedule at equal
  comfort (**+1.60 %**), a worst case under 1 % (**−0.78 %**) and top-tier reward regret (**−0.065** mean, **−0.26** worst).
  It is also the most accurate recovery-time predictor in the offline replay (MAE 29 min vs 36-39 min for the PNNL models).
  PNNL's deployed median-of-four is the runner-up (+1.76 % / −0.61 %) with almost twice the reward regret (−0.12 / −0.47).
* **Optimal stop: first-order coast** with a 0.2 °F guard: **+3.0 %** evening energy for +0.7 °F·min/zone of comfort deficit.

**Caveat:** in this simulator, start time is mostly an energy-vs-comfort dial. Learned models save 4-14 % of morning energy
vs a fixed 2-hour start, but they are late more often (EMA 43 % of mornings vs 34 % for a fixed 120-min start). That's why the
winner is picked on savings *beyond* the fixed-schedule curve, reward regret and the worst scenario, not on raw savings.

### How the winner is picked
* **Savings beyond schedule:** per scenario, the fixed 60/120/180-min runs define the energy-vs-comfort curve. An algorithm's
  score is the extra morning energy it saves compared with a fixed schedule giving the same comfort (12 scenarios have all three
  anchors).
* **Reward regret:** per scenario, the algorithm's simulator reward (comfort + energy + carbon) minus the best algorithm's (0 = best).
* **Worst case:** the worst scenario on both.

### Start leaderboard (sorted by mean reward regret)

| start algorithm | scenarios | savings beyond schedule % (mean) | … worst scenario | reward regret (mean) | … worst | late % (1 °F tol.) | unmet °F·min/zone | energy saved vs fixed 120 % |
|---|---|---|---|---|---|---|---|---|
| Fixed 60 min | 12 | 0.00 | 0.00 | -0.022 | -0.086 | 57.7 | 51.1 | 9.2 |
| PNNL M4 · exponential | 22 | -0.40 | -9.48 | -0.033 | -0.174 | 45.1 | 64.5 | 13.8 |
| G36 recovery learner (NeurIPS v7) | 22 | -0.83 | -6.04 | -0.062 | -0.243 | 46.9 | 55.9 | 4.2 |
| **Linear-rate EMA (ours)** | 22 | 1.60 | -0.78 | -0.065 | -0.259 | 42.6 | 55.5 | 8.5 |
| Fixed 120 min | 22 | 0.00 | -0.00 | -0.081 | -0.260 | 33.9 | 49.0 | 0.0 |
| G36 learned rate (NeurIPS v6) | 22 | 0.17 | -1.49 | -0.082 | -0.260 | 34.0 | 49.1 | 0.2 |
| PNNL deployed (median of M1-M4) | 22 | 1.76 | -0.61 | -0.119 | -0.470 | 40.0 | 50.6 | 3.7 |
| SGD regression | 6 | 0.11 | -1.74 | -0.133 | -0.447 | 48.5 | 57.9 | 4.0 |
| Robust RLS | 22 | 0.21 | -4.22 | -0.142 | -0.513 | 40.8 | 50.1 | 3.2 |
| SAC reinforcement learning | 22 | -8.73 | -29.58 | -0.145 | -0.501 | 46.3 | 59.9 | -2.5 |
| PNNL M2 · OAT ratio | 6 | 0.49 | -0.58 | -0.148 | -0.501 | 47.8 | 56.4 | 3.6 |
| Robust RLS + feedback | 22 | -0.69 | -10.47 | -0.161 | -0.557 | 41.5 | 46.2 | -1.6 |
| PNNL M3 · regression | 6 | 0.33 | -1.31 | -0.168 | -0.520 | 45.9 | 51.4 | 0.1 |
| Fixed 180 min | 12 | 0.00 | 0.00 | -0.169 | -0.544 | 48.6 | 35.6 | -8.5 |
| PNNL M1 · quadratic | 6 | 0.29 | -1.09 | -0.181 | -0.520 | 47.3 | 51.3 | -0.1 |
| Static rate + 15 min | 6 | 0.35 | -0.07 | -0.182 | -0.544 | 47.3 | 47.9 | -4.2 |

*Late % uses PNNL's 1 °F allowable deviation. Unmet = comfort deficit over the first 2 h of occupancy. Energy and reward are
over 4 h before to 2 h after occupancy, paired with the fixed 120-min run on the same day. The first 7 days of every run are
learning warm-up and are not scored. Algorithms run on 6 or 12 scenarios aren't comparable on the worst case.*

### Head-to-head on the 6 scenarios where all four PNNL models ran

| algorithm | savings beyond schedule % (mean) | … worst | reward regret (mean) | late % (1 °F tol.) | unmet °F·min/zone |
|---|---|---|---|---|---|
| **Linear-rate EMA (ours)** | 0.73 | -0.78 | -0.089 | 49.7 | 62.0 |
| PNNL M1 · quadratic | 0.29 | -1.09 | -0.181 | 45.9 | 53.0 |
| PNNL M2 · OAT ratio | 0.49 | -0.58 | -0.148 | 47.4 | 57.7 |
| PNNL M3 · regression | 0.33 | -1.31 | -0.168 | 43.7 | 53.2 |
| PNNL M4 · exponential | 0.28 | -4.02 | -0.041 | 52.2 | 71.1 |
| PNNL deployed (median of M1-M4) | 0.67 | -0.55 | -0.152 | 46.4 | 55.6 |
| Fixed 120 min | 0.00 | 0.00 | -0.078 | 36.3 | 54.3 |

### Offline replay: predicted vs actual recovery time (1,033 recorded recoveries)

| model | MAE (min) | bias (min) | late starts % | within ±15 min % |
|---|---|---|---|---|
| PNNL M1 · quadratic | 38.9 | +10.8 | 23.2 | 54.5 |
| PNNL M2 · OAT ratio | 36.2 | +0.3 | 26.1 | 61.5 |
| PNNL M3 · regression | 39.1 | +12.8 | 26.9 | 51.5 |
| PNNL M4 · exponential | 35.8 | -22.6 | 58.4 | 69.3 |
| Linear-rate EMA (ours) | 28.9 | -14.1 | 25.8 | 62.1 |

### Optimal stop (fixed 120-min start, 0.2 °F guard, one building in Atlanta, Denver, Minneapolis and Phoenix)

| stop algorithm | days stopped early % | restarts/day | unmet last 3 h °F·min/zone | evening energy saved % | reward gain |
|---|---|---|---|---|---|
| **First-order coast (ours)** | 5.7 | 0.43 | 12.56 | 3.01 | -0.009 |
| Constant drift 0.35 °F/h | 2.1 | 0.69 | 17.58 | 5.71 | -0.050 |
| G36 recovery-rate proxy | 0.6 | 0.00 | 11.68 | -0.05 | +0.004 |
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
