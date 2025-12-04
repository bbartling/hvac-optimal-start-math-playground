
# AGENTS_HVAC_v2.md — Token‑Optimized Specification for AI Agents Implementing HVAC Optimal‑Start Algorithms

## 1. Purpose
This document is a **machine‑optimized**, **deterministic**, **non‑ambiguous** reference for AI agents implementing HVAC optimal‑start algorithms.  
It is aligned with the PNNL research paper *Optimal Start Control for ACs and HPs*.  
Human readability is maintained, but the priority is **mathematical clarity for AI reasoning**.

---

# 2. Canonical Variables (Normalized Glossary)

T_z0     = initial zone temperature  
T_sp     = occupied setpoint temperature  
ΔT       = T_sp − T_z0  
t_act    = actual warm‑up duration (minutes)  
t_pred   = predicted warm‑up duration (minutes)  
OAT      = outdoor air temperature  
WF       = weather factor  
ω        = smoothing weight (0 < ω < 1)  
a,b,d    = model coefficients  
x        = feature term  
x1       = ΔT  
x2       = ΔT * WF  
DB       = comfort deadband  

Warm‑up success criterion:
T_zone >= T_sp − DB

---

# 3. Model Definitions

## Model 0 — Linear EMA Model
t_pred = ΔT / R  
R_new  = R_old + ω*((ΔT/t_act) − R_old)

---

## Model 1 — Quadratic Model
x = ΔT²  
t_pred = a*x + b

Coefficient update:
a_today = t_act / x  
a_new   = a_old + ω*(a_today − a_old)

Two‑point solution:
t1 = a*x1 + b  
t2 = a*x2 + b

---

## Model 3 — Weather‑Adjusted Regression
x1 = ΔT  
x2 = ΔT * WF  

t_pred = a*x1 + b*x2 + d  

Single‑point update:
a_today = (t_act − d_old)/ΔT − b_old*WF  
a_new   = a_old + ω*(a_today − a_old)

Full 3×3 solve (when updating a,b,d simultaneously):
t_i = a*x1_i + b*x2_i + d  for i=1..3

---

# 4. Weather Factor (WF)

WF = clamp( (T_sp − OAT)/α3c , 0 , 1 )

---

# 5. Skip Conditions (Learning Disabled)

Learning is skipped if:
ΔT <= 0  
t_act <= 0  
sensor faults  
setpoint changes during warm‑up  
weekend/holiday warm‑up anomalies  

---

# 6. Output Constraints

0 ≤ t_pred ≤ t_max  

---

# 7. Smoothing Weight

0.05 ≤ ω ≤ 0.25  

---

# 8. Prediction Algorithm (Deterministic)

ΔT = T_sp − T_z0  
WF = compute_WF(OAT)

Model selection heuristic:
- If strong weather correlation → use Model 3  
- Else if quadratic curvature fits → Model 1  
- Else → Model 0  

Prediction:
Model 3: t_pred = a*ΔT + b*(ΔT*WF) + d  
Model 1: t_pred = a*(ΔT²) + b  
Model 0: t_pred = ΔT / R  

Start_time = Occupancy_start − t_pred

---

# 9. Learning Algorithm

If skip conditions are FALSE:

## Model 0:
observed_R = ΔT / t_act  
R = R + ω*(observed_R − R)

## Model 1:
x = ΔT²  
a_today = t_act / x  
a = a + ω*(a_today − a)

## Model 3 (single‑point):
a_today = (t_act − d)/ΔT − b*WF  
a = a + ω*(a_today − a)

## Model 3 (full update):
Solve 3×3 for (a_today,b_today,d_today)  
θ_new = θ_old + ω*(θ_today − θ_old)

---

# 10. Error Metrics

Absolute Error = |t_act − t_pred|  
Relative Error = (t_act − t_pred)/t_act  
MAE = mean(|errors|)

Model switching:
If MAE_Model3 < MAE_Model1 → prefer Model 3  
If Model1 < Model0 → prefer Model 1  

---

# 11. Fallback Rules

If WF unavailable → use Model 1  
If ΔT unusually large → penalty term added  
If predictions oscillate → reduce ω  

---

# 12. Minimal Pseudocode

def optimal_start(T_z0, T_sp, OAT, occ):
    ΔT = T_sp - T_z0
    if ΔT <= 0: return occ
    WF = compute_WF(OAT)
    if model3:
        t_pred = a*ΔT + b*(ΔT*WF) + d
    elif model1:
        t_pred = a*(ΔT**2) + b
    else:
        t_pred = ΔT / R
    return occ - t_pred

---

# 13. Notes for AI Agents

Use exact formulas.  
Avoid hallucinating variables.  
Always apply smoothing.  
Default to Model 1 if uncertainty exists.  
Never update coefficients when data is invalid.  

End of AGENTS_HVAC_v2.md.
