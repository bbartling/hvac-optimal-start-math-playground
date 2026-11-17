# hvac-optimal-start-math-playground → `hvac_optimal`

Data-driven **optimal start** and **optimal stop** for HVAC, in pure Python with no
dependencies. Every algorithm was benchmarked closed loop on the NeurIPS 2026
smart-buildings simulator, across many buildings, AHUs, zones, climates and seasons.

> **Status:** the benchmark is still running. The tables below are interim but already
> validated: every number comes from complete 30-day simulator runs. The defaults in the
> package will be set from the final tables.

## What the benchmark says so far (plain English)

1. **Optimal start in this simulator is mostly an energy-vs-comfort dial.** All
   start algorithms, including the 4 PNNL models, the repo models, robust RLS and the
   neurips v6/v7/SAC controllers, land close to the trade-off curve you get from fixed
   60/120/180-minute schedules. Starting later saves 3–9 % of morning HVAC cost in
   cooling climates, at the price of +1–7 K·min per zone of comfort deficit in the first
   two hours. **So far, no algorithm consistently beats a well-chosen fixed schedule at
   equal comfort** (see "savings beyond schedule").
2. **Cold climates are capacity-limited.** In Fairbanks and Minneapolis in January the
   air handlers run all night on setback heating, and some zones reach the band only
   hours after occupancy, whatever the start time. No start algorithm can fix that.
   Starting earlier buys comfort with energy, roughly linearly.
3. **Cooling climates recover fast** (2 °F in 10–15 min). Late comfort comes from zones
   drifting back out after occupancy (solar and internal gains), not from late starts.
   Longer pre-cooling (fixed_120) stores cooling in the building mass, and the
   simulator's own reward slightly prefers it.
4. **Early stop with a 0.5 K (0.9 °F) guard never fires.** This is the guard the neurips
   v6 controller uses. The G36 sequence holds zones only 0.4 K inside the band, so no
   projection clears it. With a 0.2 °F guard, the first-order coast model stops on about
   14 % of AHU-days and saves about 8 % of end-of-day energy, at a small comfort cost
   (interim: one scenario so far).
5. **The neurips controllers, evaluated as unproven candidates:**
   - v6 ties the fixed 120-minute schedule (its 120-minute cap binds).
   - v7 and SAC trim are not better on comfort at equal energy.
   - SAC trim was trained on 24 of the 30 training scenarios, so its scores there are
     optimistic.
   - sac_full with a zero actor is identical to v7.
   - The DQN controller exists only as a spec.

## Layout

| path | what |
|---|---|
| `src/hvac_optimal/` | the package: start models, stop models, multi-zone planners |
| `tests/` | pytest suite (PNNL equations, PNNL EMA vs aems-edge, planners, stop bounds) |
| `benchmarks/neurips_sim/` | closed-loop simulator harness and analysis ([README](benchmarks/neurips_sim/README.md)) |
| `examples/quickstart.py` | a minimal start + stop loop |
| `docs/LEARN_THE_MATH.md` | the original learning guide (formerly this README) |
| `lessons/`, `README_LESSON_DETAILS.md` | the 50-day lessons |
| `archive/` | the original tutorial scripts, unchanged ([README](archive/README.md)) |
| `PNNL_Paper/` | the reference paper |

## Quick start

```bash
pip install -e .[dev]
pytest
python examples/quickstart.py
python -m hvac_optimal          # lists algorithms and recommended defaults
```

```python
from hvac_optimal import OptimalStartPlanner, OptimalStopPlanner, ZoneReading

start = OptimalStartPlanner.recommended()
zones = [ZoneReading("vav-1", temp=64.0, heat_sp=70.0, cool_sp=75.0)]
if start.should_start(minutes_to_occupancy=45, zones=zones, oat=20.0):
    ...  # command the AHU / RTU on (warm-up)
```

## License

MIT, see [LICENSE](LICENSE).

## Results

<!-- RESULTS:START -->

_Interim results, 2026-11-16 22:45 CST. The first 7 days of each run are learning warm-up and are not scored. Energy and reward are paired against fixed_120 on the same scenario-day. Unmet = band deficit summed over the first 2 h of occupancy, per zone (K·min). Late (1F tol) = share of AHU-days on which a recoverable zone was more than 1 °F outside the band at occupancy._

**Coverage:** runs: 62, scenarios: 6, buildings: 2, climates: 5, AHU-days (scored): 5808, zones per scenario: 39-85

### Start: evidence used to pick the winner

Scenarios: 6. Arms run on fewer scenarios are not comparable on the worst case.

| start | scenarios | savings beyond schedule % (mean) | savings beyond schedule % (worst scenario) | reward regret (mean) | reward regret (worst) |
|---|---|---|---|---|---|
| fixed_60 | 4 | 0.00 | 0.00 | -0.02 | -0.09 |
| pnnl_m4_exponential | 4 | -0.86 | -4.02 | -0.03 | -0.09 |
| fixed_120 | 6 | 0.00 | 0.00 | -0.09 | -0.26 |
| m0_linear_ema | 5 | 0.12 | -0.78 | -0.11 | -0.26 |
| v7 | 4 | -0.37 | -0.64 | -0.12 | -0.21 |
| v6 | 4 | 0.20 | 0.00 | -0.13 | -0.26 |
| sac_trim | 4 | -0.06 | -1.63 | -0.16 | -0.41 |
| vavrl_static | 4 | -2.84 | -8.69 | -0.17 | -0.54 |
| repo_m5_sgd | 3 | -1.34 | -3.56 | -0.19 | -0.45 |
| pnnl_m3_regression | 3 | -1.54 | -2.68 | -0.20 | -0.52 |
| robust_rls_fb | 6 | -2.15 | -4.65 | -0.20 | -0.56 |
| pnnl_m2_oat_ratio | 3 | -1.00 | -2.65 | -0.21 | -0.50 |
| pnnl_m1_quadratic | 3 | -1.21 | -2.39 | -0.21 | -0.52 |
| robust_rls | 5 | -1.11 | -2.72 | -0.23 | -0.51 |
| pnnl_deployed_median_split | 4 | -0.87 | -2.21 | -0.23 | -0.47 |

### Savings beyond a fixed schedule at equal comfort, per scenario (%)

| scenario | fixed_120 | fixed_60 | m0_linear_ema | pnnl_deployed_median_split | pnnl_m1_quadratic | pnnl_m2_oat_ratio | pnnl_m3_regression | pnnl_m4_exponential | repo_m5_sgd | robust_rls | robust_rls_fb | sac_trim | v6 | v7 | vavrl_static |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| building_train_1/fairbanks_1 | 0.00 | 0.00 | -0.78 | -2.21 | -2.39 | -2.65 | -2.68 | 0.50 | -3.56 | -2.72 | -3.22 | -1.63 | 0.00 | -0.64 | -3.35 |
| building_train_1/minneapolis_1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| building_train_1/phoenix_5 | 0.00 | 0.00 | 0.27 | 0.17 | -0.66 | 0.22 | -1.31 | 0.94 | 0.16 | -0.04 | -1.04 | 0.92 | 0.54 | -0.43 | 0.76 |
| building_train_2/denver_8 | 0.00 | 0.00 | 1.63 |  |  |  |  |  |  |  | -4.65 |  |  |  | -8.69 |
| building_train_2/minneapolis_6 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| building_train_2/singapore_1 | 0.00 | 0.00 | -0.62 | -0.55 | -0.59 | -0.57 | -0.63 | -4.02 | -0.61 | -0.58 | 0.30 | 0.52 | 0.06 | -0.03 | -0.07 |

### Start: mean over scenarios (each scenario weighted equally)

| start | late % (1F tol) | late p90 (1F tol) | unmet K*min/zone | unmet w/ people K*min/zone | energy saved vs fixed120 % | reward gain vs fixed120 | scenarios |
|---|---|---|---|---|---|---|---|
| pnnl_m4_exponential | 64.93 | 272.50 | 49.14 | 57.32 | 9.75 | 0.09 | 4 |
| fixed_60 | 51.95 | 164.63 | 36.08 | 41.47 | 7.79 | 0.05 | 4 |
| v7 | 52.34 | 261.75 | 41.89 | 48.97 | 2.65 | 0.01 | 4 |
| fixed_120 | 36.34 | 178.08 | 28.67 | 33.84 | 0.00 | 0.00 | 6 |
| m0_linear_ema | 60.00 | 235.80 | 38.92 | 45.65 | 7.00 | -0.00 | 5 |
| v6 | 46.88 | 248.38 | 39.15 | 46.31 | 0.55 | -0.00 | 4 |
| sac_trim | 52.73 | 196.50 | 42.04 | 50.11 | -0.13 | -0.03 | 4 |
| vavrl_static | 39.76 | 131.75 | 26.68 | 31.71 | -4.43 | -0.10 | 4 |
| pnnl_deployed_median_split | 57.03 | 259.62 | 38.67 | 46.00 | 0.31 | -0.10 | 4 |
| repo_m5_sgd | 46.35 | 173.17 | 35.11 | 40.99 | 1.65 | -0.10 | 3 |
| robust_rls_fb | 39.67 | 171.67 | 26.41 | 31.38 | -3.42 | -0.11 | 6 |
| pnnl_m3_regression | 37.50 | 162.83 | 33.12 | 39.09 | -0.57 | -0.12 | 3 |
| pnnl_m2_oat_ratio | 46.35 | 165.67 | 35.11 | 41.53 | 2.05 | -0.12 | 3 |
| pnnl_m1_quadratic | 42.19 | 165.67 | 33.17 | 39.24 | -0.07 | -0.13 | 3 |
| robust_rls | 46.22 | 201.50 | 31.18 | 36.95 | 0.07 | -0.13 | 5 |

### Start by climate

| start | city | AHU-days | lead p50 | late % (1F tol) | late p90 (1F tol) | unmet K*min/zone | unmet w/ people K*min/zone | energy saved vs fixed120 % | reward gain vs fixed120 |
|---|---|---|---|---|---|---|---|---|---|
| fixed_60 | denver | 144 | 55.00 | 87.50 | 108.50 | 22.22 | 24.91 | 12.79 | 0.03 |
| m0_linear_ema | denver | 144 | 32.50 | 56.25 | 105.00 | 23.05 | 25.66 | 15.85 | 0.03 |
| fixed_120 | denver | 144 | 115.00 | 30.56 | 75.00 | 14.80 | 17.37 | 0.00 | 0.00 |
| robust_rls_fb | denver | 144 | 165.00 | 51.39 | 63.50 | 13.97 | 16.59 | -6.08 | -0.04 |
| vavrl_static | denver | 144 | 180.00 | 65.28 | 43.50 | 12.78 | 15.33 | -12.16 | -0.06 |
| fixed_60 | fairbanks | 64 | 360.00 | 100.00 | 545.00 | 98.57 | 116.19 | 9.67 | 0.24 |
| pnnl_m4_exponential | fairbanks | 64 | 360.00 | 100.00 | 540.00 | 98.17 | 115.75 | 9.89 | 0.23 |
| v7 | fairbanks | 64 | 360.00 | 96.88 | 507.50 | 89.46 | 106.29 | 2.70 | 0.07 |
| fixed_120 | fairbanks | 64 | 360.00 | 96.88 | 503.00 | 84.65 | 101.64 | 0.00 | 0.00 |
| v6 | fairbanks | 64 | 360.00 | 96.88 | 503.00 | 84.65 | 101.64 | 0.00 | 0.00 |
| sac_trim | fairbanks | 64 | 302.50 | 98.44 | 422.50 | 85.81 | 101.79 | -0.83 | -0.00 |
| m0_linear_ema | fairbanks | 64 | 360.00 | 95.31 | 522.00 | 85.44 | 102.45 | -0.23 | -0.02 |
| repo_m5_sgd | fairbanks | 64 | 360.00 | 92.19 | 504.50 | 79.71 | 95.46 | -6.99 | -0.21 |
| pnnl_deployed_median_split | fairbanks | 64 | 360.00 | 92.19 | 488.00 | 78.52 | 94.97 | -6.47 | -0.23 |
| pnnl_m2_oat_ratio | fairbanks | 64 | 360.00 | 90.62 | 482.00 | 78.92 | 95.99 | -6.63 | -0.26 |
| robust_rls | fairbanks | 64 | 360.00 | 90.62 | 482.00 | 77.03 | 93.68 | -8.01 | -0.28 |
| pnnl_m3_regression | fairbanks | 64 | 360.00 | 95.31 | 483.50 | 76.82 | 93.28 | -8.12 | -0.28 |
| pnnl_m1_quadratic | fairbanks | 64 | 360.00 | 95.31 | 482.00 | 76.42 | 92.94 | -8.11 | -0.28 |
| robust_rls_fb | fairbanks | 64 | 180.00 | 92.19 | 482.00 | 75.76 | 92.05 | -9.39 | -0.29 |
| vavrl_static | fairbanks | 64 | 360.00 | 93.75 | 483.50 | 75.59 | 91.88 | -9.65 | -0.31 |
| pnnl_m4_exponential | minneapolis | 64 | 37.50 | 100.00 | 535.00 | 70.59 | 82.89 | 15.16 | 0.26 |
| m0_linear_ema | minneapolis | 64 | 85.00 | 98.44 | 537.00 | 59.42 | 71.11 | 6.19 | 0.10 |
| v7 | minneapolis | 64 | 115.00 | 95.31 | 527.50 | 55.20 | 65.46 | 1.72 | 0.05 |
| fixed_120 | minneapolis | 208 | 115.00 | 27.88 | 255.00 | 18.01 | 21.20 | 0.00 | 0.00 |
| v6 | minneapolis | 64 | 115.00 | 90.62 | 490.50 | 53.71 | 64.21 | 0.00 | 0.00 |
| pnnl_deployed_median_split | minneapolis | 64 | 180.00 | 95.31 | 535.50 | 52.56 | 63.52 | -1.91 | -0.11 |
| robust_rls | minneapolis | 208 | 10.00 | 29.81 | 253.00 | 18.06 | 21.18 | -1.32 | -0.13 |
| sac_trim | minneapolis | 64 | 115.00 | 89.06 | 358.50 | 67.62 | 81.32 | 2.35 | -0.15 |
| robust_rls_fb | minneapolis | 208 | 82.50 | 28.37 | 221.00 | 16.45 | 19.44 | -3.96 | -0.16 |
| sac_trim | phoenix | 64 | 20.00 | 23.44 | 5.00 | 11.26 | 13.55 | -0.33 | 0.02 |
| fixed_120 | phoenix | 64 | 125.00 | 0.00 | 0.00 | 12.46 | 13.37 | 0.00 | 0.00 |
| vavrl_static | phoenix | 64 | 120.00 | 0.00 | 0.00 | 13.16 | 14.28 | 1.49 | -0.00 |
| v6 | phoenix | 64 | 110.00 | 0.00 | 0.00 | 13.94 | 14.97 | 2.09 | -0.01 |
| robust_rls_fb | phoenix | 64 | 115.00 | 3.12 | 0.00 | 14.05 | 15.00 | 0.62 | -0.03 |
| pnnl_m3_regression | phoenix | 64 | 60.00 | 17.19 | 5.00 | 17.00 | 18.26 | 3.42 | -0.05 |
| pnnl_deployed_median_split | phoenix | 64 | 20.00 | 40.62 | 15.00 | 17.77 | 19.48 | 5.70 | -0.05 |
| robust_rls | phoenix | 64 | 20.00 | 45.31 | 15.00 | 18.91 | 20.62 | 6.69 | -0.06 |
| pnnl_m1_quadratic | phoenix | 64 | 22.50 | 31.25 | 15.00 | 17.44 | 18.95 | 4.53 | -0.07 |
| fixed_60 | phoenix | 64 | 55.00 | 20.31 | 5.00 | 18.39 | 19.47 | 6.18 | -0.07 |
| pnnl_m4_exponential | phoenix | 64 | 0.00 | 56.25 | 15.00 | 20.45 | 23.15 | 9.27 | -0.08 |
| v7 | phoenix | 64 | 20.00 | 17.19 | 12.00 | 18.48 | 19.61 | 5.85 | -0.08 |
| repo_m5_sgd | phoenix | 64 | 10.00 | 46.88 | 15.00 | 19.61 | 21.34 | 7.62 | -0.08 |
| m0_linear_ema | phoenix | 64 | 7.50 | 50.00 | 15.00 | 20.71 | 22.86 | 8.87 | -0.08 |
| pnnl_m2_oat_ratio | phoenix | 64 | 10.00 | 48.44 | 15.00 | 20.44 | 22.46 | 8.54 | -0.08 |
| sac_trim | singapore | 144 | 105.00 | 0.00 | 0.00 | 3.49 | 3.76 | -1.71 | 0.00 |
| fixed_120 | singapore | 144 | 115.00 | 0.00 | 0.00 | 4.27 | 4.38 | 0.00 | 0.00 |
| v6 | singapore | 144 | 115.00 | 0.00 | 0.00 | 4.30 | 4.42 | 0.13 | -0.00 |
| v7 | singapore | 144 | 115.00 | 0.00 | 0.00 | 4.40 | 4.53 | 0.33 | -0.00 |
| robust_rls_fb | singapore | 144 | 55.00 | 0.00 | 0.00 | 4.96 | 5.05 | 2.26 | -0.01 |
| fixed_60 | singapore | 144 | 55.00 | 0.00 | 0.00 | 5.15 | 5.30 | 2.50 | -0.01 |
| vavrl_static | singapore | 144 | 55.00 | 0.00 | 0.00 | 5.21 | 5.36 | 2.59 | -0.01 |
| pnnl_m3_regression | singapore | 144 | 12.50 | 0.00 | 0.00 | 5.54 | 5.72 | 2.99 | -0.02 |
| pnnl_m1_quadratic | singapore | 144 | 10.00 | 0.00 | 0.00 | 5.66 | 5.83 | 3.36 | -0.02 |
| pnnl_deployed_median_split | singapore | 144 | 10.00 | 0.00 | 0.00 | 5.84 | 6.01 | 3.93 | -0.02 |
| robust_rls | singapore | 144 | 10.00 | 0.00 | 0.00 | 5.99 | 6.17 | 4.32 | -0.03 |
| pnnl_m2_oat_ratio | singapore | 144 | 10.00 | 0.00 | 0.00 | 5.95 | 6.13 | 4.23 | -0.03 |
| repo_m5_sgd | singapore | 144 | 10.00 | 0.00 | 0.00 | 6.00 | 6.17 | 4.31 | -0.03 |
| m0_linear_ema | singapore | 144 | 10.00 | 0.00 | 0.00 | 6.00 | 6.18 | 4.31 | -0.03 |
| pnnl_m4_exponential | singapore | 144 | 0.00 | 3.47 | 0.00 | 7.33 | 7.51 | 4.70 | -0.04 |

### Start by season

| start | season | AHU-days | lead p50 | late % (1F tol) | late p90 (1F tol) | unmet K*min/zone | unmet w/ people K*min/zone | energy saved vs fixed120 % | reward gain vs fixed120 |
|---|---|---|---|---|---|---|---|---|---|
| sac_trim | cooling | 208 | 95.00 | 7.21 | 0.00 | 5.88 | 6.78 | -1.02 | 0.01 |
| fixed_120 | cooling | 343 | 115.00 | 0.00 | 0.00 | 4.97 | 5.21 | 0.00 | 0.00 |
| v6 | cooling | 208 | 115.00 | 0.00 | 0.00 | 7.26 | 7.66 | 1.11 | -0.01 |
| vavrl_static | cooling | 208 | 55.00 | 0.00 | 0.00 | 7.65 | 8.10 | 2.04 | -0.01 |
| robust_rls_fb | cooling | 343 | 65.00 | 0.58 | 0.00 | 5.89 | 6.13 | 1.83 | -0.02 |
| pnnl_m3_regression | cooling | 208 | 20.00 | 5.29 | 0.00 | 9.07 | 9.58 | 3.20 | -0.03 |
| pnnl_deployed_median_split | cooling | 208 | 10.00 | 12.50 | 5.00 | 9.51 | 10.16 | 4.81 | -0.04 |
| v7 | cooling | 208 | 110.00 | 5.29 | 0.00 | 8.73 | 9.17 | 3.09 | -0.04 |
| fixed_60 | cooling | 208 | 55.00 | 6.25 | 0.00 | 9.22 | 9.66 | 4.34 | -0.04 |
| robust_rls | cooling | 343 | 10.00 | 8.45 | 0.00 | 7.53 | 7.96 | 4.72 | -0.04 |
| pnnl_m1_quadratic | cooling | 208 | 10.00 | 9.62 | 0.00 | 9.28 | 9.87 | 3.95 | -0.05 |
| repo_m5_sgd | cooling | 208 | 10.00 | 14.42 | 5.00 | 10.19 | 10.84 | 5.97 | -0.05 |
| m0_linear_ema | cooling | 208 | 10.00 | 15.38 | 8.00 | 10.53 | 11.31 | 6.59 | -0.05 |
| pnnl_m2_oat_ratio | cooling | 208 | 10.00 | 14.90 | 8.00 | 10.41 | 11.15 | 6.39 | -0.05 |
| pnnl_m4_exponential | cooling | 208 | 0.00 | 19.71 | 15.00 | 11.37 | 12.32 | 6.99 | -0.06 |
| pnnl_m4_exponential | heating | 128 | 55.00 | 100.00 | 540.00 | 84.38 | 99.32 | 12.52 | 0.25 |
| fixed_60 | heating | 127 | 55.00 | 96.85 | 460.00 | 64.15 | 75.84 | 10.23 | 0.17 |
| v7 | heating | 128 | 115.00 | 96.09 | 521.00 | 72.33 | 85.87 | 2.21 | 0.06 |
| m0_linear_ema | heating | 191 | 100.00 | 89.01 | 480.00 | 58.45 | 69.95 | 4.75 | 0.04 |
| fixed_120 | heating | 191 | 130.00 | 75.92 | 445.00 | 53.21 | 64.08 | 0.00 | 0.00 |
| v6 | heating | 128 | 115.00 | 93.75 | 501.00 | 69.18 | 82.93 | 0.00 | 0.00 |
| sac_trim | heating | 128 | 115.00 | 93.75 | 393.00 | 76.72 | 91.56 | 0.76 | -0.08 |
| pnnl_deployed_median_split | heating | 128 | 260.00 | 93.75 | 515.00 | 65.54 | 79.25 | -4.19 | -0.17 |
| repo_m5_sgd | heating | 64 | 360.00 | 92.19 | 504.50 | 79.71 | 95.46 | -6.99 | -0.21 |
| vavrl_static | heating | 127 | 180.00 | 85.83 | 402.00 | 47.28 | 57.97 | -10.27 | -0.23 |
| robust_rls_fb | heating | 191 | 180.00 | 82.20 | 440.00 | 47.35 | 57.82 | -10.10 | -0.25 |
| robust_rls | heating | 128 | 290.00 | 92.19 | 500.00 | 63.59 | 77.18 | -7.68 | -0.26 |
| pnnl_m2_oat_ratio | heating | 64 | 360.00 | 90.62 | 482.00 | 78.92 | 95.99 | -6.63 | -0.26 |
| pnnl_m3_regression | heating | 64 | 360.00 | 95.31 | 483.50 | 76.82 | 93.28 | -8.12 | -0.28 |
| pnnl_m1_quadratic | heating | 64 | 360.00 | 95.31 | 482.00 | 76.42 | 92.94 | -8.11 | -0.28 |
| robust_rls | shoulder | 9 | 10.00 | 22.22 | 15.00 | 4.11 | 0.00 | 29.89 | 0.07 |
| fixed_60 | shoulder | 81 | 55.00 | 82.72 | 55.00 | 16.81 | 17.17 | 13.80 | 0.04 |
| m0_linear_ema | shoulder | 81 | 30.00 | 43.21 | 35.00 | 17.60 | 17.81 | 18.19 | 0.03 |
| fixed_120 | shoulder | 90 | 115.00 | 21.11 | 25.00 | 9.30 | 9.74 | 0.00 | 0.00 |
| robust_rls_fb | shoulder | 90 | 125.00 | 38.89 | 20.50 | 9.26 | 9.61 | -2.05 | -0.02 |
| vavrl_static | shoulder | 81 | 180.00 | 55.56 | 15.00 | 8.32 | 8.96 | -12.54 | -0.05 |

### Start on post-weekend / post-holiday days (Monday problem)

| start | post_weekend | AHU-days | lead p50 | lead p90 | late % (1F tol) | late p90 (1F tol) | late % | late p90 min | late p99 min | early waste min | unmet K*min/zone | unmet p95 | unmet w/ people K*min/zone | prestart run min | energy saved vs fixed120 % | energy saved $/day | reward gain vs fixed120 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| pnnl_m4_exponential | False | 252 | 0.00 | 290.00 | 50.40 | 384.50 | 82.54 | 514.50 | 727.45 | 0.08 | 39.22 | 117.07 | 48.59 | 188.69 | 10.06 | 3.84 | 0.08 |
| fixed_60 | False | 312 | 55.00 | 159.50 | 48.40 | 174.00 | 64.74 | 229.50 | 691.70 | 12.13 | 26.90 | 113.04 | 32.45 | 178.57 | 7.86 | 2.59 | 0.04 |
| m0_linear_ema | False | 360 | 20.00 | 155.50 | 48.61 | 320.00 | 63.89 | 375.50 | 709.10 | 0.32 | 30.47 | 97.49 | 37.21 | 177.94 | 7.27 | 1.96 | 0.00 |
| fixed_120 | False | 468 | 115.00 | 210.00 | 25.21 | 165.00 | 38.03 | 245.00 | 685.00 | 46.36 | 20.28 | 90.93 | 25.22 | 203.11 | 0.00 | 0.00 | 0.00 |
| v7 | False | 252 | 115.00 | 336.50 | 38.89 | 364.50 | 53.57 | 484.50 | 727.35 | 36.03 | 32.48 | 108.84 | 40.74 | 232.64 | 2.31 | 0.96 | -0.00 |
| v6 | False | 252 | 115.00 | 259.50 | 34.92 | 349.50 | 53.17 | 454.50 | 712.15 | 39.03 | 30.65 | 103.85 | 38.76 | 238.95 | 0.45 | 0.16 | -0.00 |
| sac_trim | False | 252 | 110.00 | 169.00 | 40.48 | 264.00 | 48.81 | 310.00 | 629.30 | 32.46 | 32.09 | 99.24 | 40.96 | 226.05 | -0.75 | -0.35 | -0.07 |
| vavrl_static | False | 312 | 145.00 | 238.00 | 35.58 | 93.50 | 53.85 | 184.50 | 652.80 | 11.15 | 19.82 | 86.10 | 24.86 | 205.26 | -4.28 | -1.65 | -0.09 |
| pnnl_deployed_median_split | False | 252 | 20.00 | 354.00 | 44.05 | 320.00 | 57.54 | 500.50 | 717.45 | 3.51 | 30.91 | 98.51 | 39.03 | 199.25 | 0.71 | -0.38 | -0.10 |
| robust_rls_fb | False | 468 | 112.50 | 180.00 | 30.98 | 136.50 | 45.30 | 216.50 | 660.00 | 20.54 | 19.01 | 78.03 | 23.69 | 180.78 | -3.84 | -1.78 | -0.11 |
| pnnl_m3_regression | False | 204 | 45.00 | 342.00 | 26.47 | 124.00 | 51.47 | 247.50 | 659.85 | 16.79 | 24.80 | 106.62 | 31.28 | 190.25 | -0.88 | -0.92 | -0.12 |
| pnnl_m2_oat_ratio | False | 204 | 10.00 | 342.00 | 32.84 | 151.00 | 49.02 | 249.00 | 659.55 | 1.00 | 26.60 | 103.24 | 33.41 | 169.63 | 2.09 | 0.16 | -0.12 |
| robust_rls | False | 360 | 10.00 | 311.50 | 30.56 | 222.50 | 43.33 | 298.00 | 697.05 | 0.35 | 22.64 | 88.66 | 28.28 | 147.19 | -0.53 | -0.74 | -0.13 |
| pnnl_m1_quadratic | False | 204 | 20.00 | 360.00 | 30.88 | 120.50 | 45.10 | 247.50 | 659.85 | 13.60 | 25.09 | 105.46 | 31.62 | 184.41 | -0.05 | -0.66 | -0.13 |
| repo_m5_sgd | False | 204 | 10.00 | 345.00 | 32.84 | 127.50 | 50.98 | 249.00 | 659.55 | 0.59 | 25.74 | 107.28 | 32.32 | 170.29 | 0.80 | -0.40 | -0.14 |
| pnnl_m4_exponential | True | 84 | 2.50 | 360.00 | 50.00 | 451.00 | 82.14 | 369.00 | 770.85 | 0.06 | 39.07 | 122.21 | 36.09 | 200.42 | 8.82 | 3.75 | 0.14 |
| sac_trim | True | 84 | 100.00 | 360.00 | 39.29 | 270.50 | 45.24 | 359.50 | 577.40 | 35.83 | 35.18 | 105.21 | 33.42 | 236.37 | 1.75 | 0.91 | 0.07 |
| fixed_60 | True | 104 | 55.00 | 360.00 | 50.00 | 181.50 | 61.54 | 208.50 | 672.45 | 11.15 | 29.16 | 115.68 | 27.98 | 195.87 | 7.56 | 2.89 | 0.06 |
| v7 | True | 84 | 115.00 | 360.00 | 42.86 | 421.00 | 52.38 | 357.50 | 728.50 | 39.35 | 34.39 | 122.04 | 31.35 | 242.20 | 3.69 | 1.60 | 0.05 |
| repo_m5_sgd | True | 68 | 10.00 | 360.00 | 32.35 | 370.00 | 42.65 | 412.50 | 689.70 | 1.18 | 28.95 | 122.69 | 26.04 | 171.91 | 4.19 | 1.29 | 0.00 |
| v6 | True | 84 | 115.00 | 360.00 | 38.10 | 389.50 | 52.38 | 363.50 | 720.10 | 40.65 | 31.45 | 106.12 | 29.06 | 248.81 | 0.87 | 0.26 | 0.00 |
| fixed_120 | True | 156 | 115.00 | 360.00 | 29.49 | 192.50 | 40.38 | 272.50 | 693.00 | 42.37 | 20.61 | 89.06 | 19.89 | 217.44 | 0.00 | 0.00 | 0.00 |
| m0_linear_ema | True | 120 | 30.00 | 306.00 | 51.67 | 277.50 | 67.50 | 352.50 | 771.20 | 0.54 | 31.77 | 113.89 | 31.33 | 200.21 | 6.17 | 1.93 | -0.01 |
| pnnl_deployed_median_split | True | 84 | 117.50 | 360.00 | 41.67 | 403.00 | 48.81 | 455.50 | 746.70 | 11.67 | 30.70 | 108.75 | 28.81 | 218.57 | -0.90 | -0.97 | -0.11 |
| vavrl_static | True | 104 | 177.50 | 360.00 | 41.35 | 127.00 | 50.00 | 162.00 | 708.80 | 12.88 | 20.05 | 94.05 | 19.40 | 221.30 | -4.90 | -2.08 | -0.12 |
| pnnl_m1_quadratic | True | 68 | 35.00 | 360.00 | 26.47 | 366.00 | 36.76 | 324.50 | 723.20 | 18.24 | 25.06 | 102.15 | 22.81 | 191.32 | -0.14 | -0.94 | -0.12 |
| pnnl_m3_regression | True | 68 | 55.00 | 360.00 | 26.47 | 365.50 | 41.18 | 507.50 | 726.55 | 21.91 | 25.63 | 101.80 | 23.26 | 195.88 | 0.35 | -0.71 | -0.12 |
| robust_rls_fb | True | 156 | 120.00 | 180.00 | 31.41 | 165.00 | 49.36 | 235.00 | 696.25 | 18.33 | 19.24 | 79.28 | 18.74 | 195.00 | -2.16 | -1.72 | -0.12 |
| robust_rls | True | 120 | 10.00 | 360.00 | 32.50 | 291.00 | 45.83 | 296.00 | 706.20 | 1.04 | 21.73 | 93.05 | 20.22 | 153.17 | 1.88 | -1.07 | -0.13 |
| pnnl_m2_oat_ratio | True | 68 | 10.00 | 360.00 | 32.35 | 373.00 | 45.59 | 504.00 | 723.20 | 1.54 | 26.33 | 101.83 | 24.22 | 172.50 | 1.92 | -0.37 | -0.14 |

### Stop (dedicated experiment: same fixed_120 start, stop guard 0.2 F)

| stop | AHU-days | early-stop min mean | stop p90 | days stopped % | restarts/day | unmet K*min/zone | unmet p95 | max excursion K p95 | energy saved vs no-stop % | energy saved $/day | reward gain vs no-stop |
|---|---|---|---|---|---|---|---|---|---|---|---|
| no_early_stop | 64 | 0.00 | 0.00 | 0.00 | 0.00 | 0.03 | 0.23 | 0.09 | 0.00 | 0.00 | 0.00 |
| first_order_coast | 64 | 1.09 | 5.00 | 14.06 | 0.83 | 0.44 | 1.10 | 0.53 | 8.28 | 0.11 | -0.01 |
| vavrl_const_drift | 64 | 0.00 | 0.00 | 0.00 | 1.00 | 0.54 | 1.09 | 0.52 | 7.62 | 0.10 | -0.01 |

| stop | city | AHU-days | early-stop min mean | stop p90 | days stopped % | restarts/day | unmet K*min/zone | unmet p95 | max excursion K p95 | energy saved vs no-stop % | energy saved $/day | reward gain vs no-stop |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| first_order_coast | denver | 64 | 1.09 | 5.00 | 14.06 | 0.83 | 0.44 | 1.10 | 0.53 | 8.28 | 0.11 | -0.01 |
| no_early_stop | denver | 64 | 0.00 | 0.00 | 0.00 | 0.00 | 0.03 | 0.23 | 0.09 | 0.00 | 0.00 | 0.00 |
| vavrl_const_drift | denver | 64 | 0.00 | 0.00 | 0.00 | 1.00 | 0.54 | 1.09 | 0.52 | 7.62 | 0.10 | -0.01 |

<!-- RESULTS:END -->
