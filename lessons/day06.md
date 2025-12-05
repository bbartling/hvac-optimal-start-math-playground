# Day 6 — Simulating Model 0 (Paper & Pencil)

**Goal:** Practice updating the Model 0 rate manually using fake data to see self‑tuning in action.

## 1. Fake Warm‑Up Data

Assume you recorded these warm‑up times:

| Day | ΔT (°F) | Minutes | Rate (°F/min) |
|----|--------|---------|---------------|
| 1  | 6      | 30      | 0.20 |
| 2  | 5      | 23      | 0.22 |
| 3  | 7      | 42      | 0.17 |

## 2. Step‑by‑Step EMA

Start with `rate_EMA = 0.20` and `α = 0.3`.  Update after each observed rate:

1. After 0.22: `rate_EMA = 0.20 + 0.3 * (0.22 - 0.20) = 0.206`
2. After 0.17: `rate_EMA = 0.206 + 0.3 * (0.17 - 0.206) ≈ 0.195`

Use a calculator to verify these numbers.

## 3. Predict Tomorrow

Suppose tomorrow’s ΔT is 8 °F and your current EMA is 0.195.  The predicted time is `t = 8 / 0.195 ≈ 41 min`.

## 4. Exercise

Repeat the process with α = 0.2 and compare the resulting EMA and prediction.

## 5. Key Takeaway

Manually updating the EMA shows how the rate gradually shifts.  Paper & pencil builds intuition.
