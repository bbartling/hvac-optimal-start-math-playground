# AGENTS_HVAC_v3.md — Token‑Optimized Specification for AI Agents Implementing HVAC Optimal‑Start Algorithms

## 1. Purpose
This document is a **machine‑optimized**, **deterministic**, **non‑ambiguous** reference for AI agents implementing HVAC optimal‑start algorithms.
It aligns with the PNNL research paper *Optimal Start Control for ACs and HPs* and the 50-Day Python Challenge curriculum.
Human readability is maintained, but the priority is **mathematical clarity for AI reasoning**.

---

# 2. Canonical Variables (Normalized Glossary)

T_z0     = initial zone temperature
T_sp     = occupied setpoint temperature
ΔT       = T_sp − T_z0
t_act    = actual warm‑up duration (minutes)
t_pred   = predicted warm‑up duration (minutes)
OAT      = outdoor air temperature
T_ref    = reference OAT (0°F heating, 100°F cooling)
WF       = weather factor (normalized load)
ω        = smoothing weight (0 < ω < 1) for EMA
η        = learning rate (for Model 5)
w        = weights vector (for Model 5)
DB       = comfort deadband (e.g., 0.5°F)
IsMon    = Boolean flag (1.0 if Monday/Holiday, else 0.0)

Warm‑up success criterion:
T_zone >= T_sp − DB

---

# 3. Model Definitions

## Model 0 — Linear EMA (Tridium kitControl)
t_pred = ΔT / R
R_new  = R_old + ω * ((ΔT / t_act) − R_old)
*Constraint: R > 0.01*

## Model 1 — Quadratic Model (Curved Physics)
x = ΔT²
t_pred = a * x + b

Coefficient update (OLS approximation):
a_today = (t_act - b_old) / x
a_new   = a_old + ω * (a_today − a_old)
b_new   = b_old + ω * ((t_act - a_new * x) - b_old)

## Model 2 — Linear + Weather Bump
base_pred = ΔT / R_base
ratio     = (T_ref - OAT_prev) / (T_ref - OAT_curr)
t_pred    = base_pred * ratio

Update:
R_observed = ΔT / t_act
R_base     = R_base + ω * (R_observed - R_base)

## Model 3 — Weather‑Adjusted Regression
x1 = ΔT
x2 = ΔT * WF
t_pred = a * x1 + b * x2 + d

Update (Recursive Least Squares or EMA):
a_today = (t_act − d_old) / x1 − b_old * WF
a_new   = a_old + ω * (a_today − a_old)

## Model 4 — Logarithmic Decay (Coasting)
t_pred = ln(DB / ΔT) / ln(α_c)

Update:
ratio_seq = [error_t / error_{t-1} for t in warmup]
α_c_today = mean(ratio_seq)
α_c_new   = α_c_old + ω * (α_c_today - α_c_old)

## Model 5 — Gradient Descent (AI Engine)
Features X = [norm(ΔT), IsMon, 1.0]
t_pred = dot(X, w)

Update (Stochastic Gradient Descent):
error = t_pred - t_act
gradient = error * X
w_new = w_old - η * gradient

---

# 4. Feature Engineering

**Weather Factor (WF):**
WF = clamp( (T_sp − OAT) / 60.0 , 0 , 1 )

**Normalization (Model 5):**
ΔT_norm = ΔT / ΔT_max_design (e.g., 20°F)

---

# 5. Skip Conditions (Learning Disabled)

Learning is skipped if:
ΔT <= 1.0
t_act <= 5.0
Sensor faults detected (NaN / Null)
Setpoint changes > 0.5° during warm‑up

---

# 6. Prediction Algorithm (Deterministic Selection)

1. Calculate ΔT = T_sp - T_z0
2. If ΔT <= 0: Return 0

3. **Model Selection Logic:**
   - [cite_start]If **Model 5** is trained & stable → Use Model 5 (Best for Mondays) [cite: 17]
   - [cite_start]Else if **OAT** variance is high → Use Model 3 [cite: 17]
   - [cite_start]Else if **Deep Setback** (ΔT > 8°F) → Use Model 1 or 4 [cite: 17]
   - [cite_start]Else → Use Model 0 (Default/Fallback) [cite: 17]

4. **Constraint:**
   t_final = clamp(t_pred, 0, t_max_allowed)

---

# 7. Learning Algorithm (Post-Run)

If skip conditions are FALSE:

**For Model 0/2:** Update Rate (R) via EMA.
**For Model 1:** Update coefficients (a, b) via EMA.
**For Model 3:** Update coefficients (a, b, d) via Matrix Solve or EMA.
**For Model 4:** Calculate decay rate, update α_c via EMA.
**For Model 5:**
   - Normalize inputs
   - Calculate Error (MSE derivative)
   - Backpropagate gradients to weights w
   - Apply Learning Rate η (default 0.01)

---

# 8. Notes for AI Agents

- **Monday Handling:** Models 0-4 require an external adder (e.g., +60 min) for Mondays. Model 5 learns this intrinsically via the `IsMon` weight.
- **Smoothing:** Never replace coefficients instantly. Always use ω (0.1–0.2) to dampen noise.
- **Safety:** If t_pred returns NaN or Infinity (e.g., log(0)), default to Model 0.
- **Persistence:** Store learned coefficients (R, a, b, w) to non-volatile memory.

