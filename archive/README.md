# archive/ — the original tutorial code (kept, unchanged)

These scripts are the original teaching versions of the optimal-start models. They are
kept exactly as they were (moved here with `git mv`, history preserved) so the lessons
still work. **New code should use the tested package in [`src/hvac_optimal`](../src/hvac_optimal/).**

| File | What it is | Package equivalent |
|---|---|---|
| `model_zero_tutorial.py` | Model 0, linear degrees-per-minute + EMA (Niagara kitControl style) | `LinearRateEMA` (`m0_linear_ema`) |
| `model_one_tutorial.py` | Model 1, quadratic | `PNNLModel1Quadratic` (`pnnl_m1_quadratic`) |
| `model_two_tutorial.py` | Model 2, OAT ratio | `PNNLModel2OatRatio` (`pnnl_m2_oat_ratio`) |
| `model_three_tutorial.py`, `model_three_tutorial_no_math_libs.py` | Model 3, weather regression | `PNNLModel3Regression` (`pnnl_m3_regression`) |
| `model_four_tutorial.py` | Model 4, exponential / first order | `PNNLModel4Exponential` (`pnnl_m4_exponential`) |
| `model_five_tutorial.py` | Model 5, gradient descent with a Monday flag | `RepoSGDModel5` (`repo_m5_sgd`) |
| `math_lesson_script.py` | the math lesson walk-through | — |
| `lessons/scripts/` | bonus-week Model 4 demos (`cd archive/lessons && python -m scripts.dayF7_model4_end_to_end`) | — |

Run any of them from this folder, e.g. `python archive/model_one_tutorial.py`.

## Known issues in the archived code (fixed in the package, left as-is here)

- `model_four_tutorial.py`: the guardrail line `c_new = clamp(c, 0.80, 0.99)` clamps the
  raw estimate `c` instead of the smoothed `c_new`, so the EMA result can leave the
  [0.80, 0.99] range (the EMA result is thrown away). Line 59 is also missing the `f`
  prefix, so it prints `{c_new}` literally. The package clamps the value it actually uses.
- The tutorials learn with simplified EMAs. PNNL's deployed agent uses a rolling window of
  daily coefficients and a specific EMA (`smoothing = min(1, 4/(n+1))`); the package
  reproduces that (`hvac_optimal._stats.pnnl_ema`, tested against the aems-edge code).
- Model 2 divides by `(T_ref - OAT_prev)`; below 0 °F (heating) or above 100 °F (cooling)
  the ratio flips sign. The package guards and clips it.
