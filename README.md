# hvac-optimal-start-math-playground

This repo teaches HVAC optimal-start math + contains Python learning playground material.

This reference outlines the consistent inputs and outputs used across `OptimalStartModel1` and `OptimalStartModel3` based on the PNNL paper in the [pdf](https://github.com/bbartling/niagara4-vibe-code-addict/tree/develop/pdf) directory.

Also see active Java versions on the vibe coder [repository](https://github.com/bbartling/niagara4-vibe-code-addict/blob/develop/README_OPT_START.md) which is actively being tested by Ben in the field in the Niagara4 framework in a `ProgramObject`.

---

<details>
<summary>📝 Model Equations Summary</summary>

The models are formulated from a simplified thermal-resistance and capacitance model (2R1C or 1R1C) of the zone dynamics.

| Model | Underlying Equation | Description |
| :--- | :--- | :--- |
| **Model 0** | $t_{opt} = \frac{T_{sp} - T_{z,0}}{r_{EMA}}$ | **Linear EMA:** Assumes a constant heating rate ($r_{EMA}$) tuned daily via Exponential Moving Average. Simple and robust for mild climates. |
| **Model 1** | $t_{opt} = \alpha_{1,a}(T_{sp} - T_{z,0})^{2} + \alpha_{1,b}$ | **Quadratic:** Assumes thermal mass is concentrated in the indoor air (1R1C model) and neglects outdoor temperature influence. Best for interior/well-insulated zones. |
| **Model 3** | $t_{opt} = \alpha_{3,a}(T_{sp} - T_{z,0}) + \alpha_{3,b}(T_{sp} - T_{z,0})\frac{(T_{sp} - T_{o})}{\alpha_{3,c}} + \alpha_{3,d}$ | **Weather Compensated:** Uses a 2R1C approximation and includes outdoor air temperature ($T_o$) influence via the second term. |

The difference in implementation stems directly from the mathematical **complexity** of the underlying models:

* **Model 0** uses a **Simple Rate** formulation ($t = \Delta T / r$), where the rate $r$ is updated via exponential smoothing ($r_{new} = \alpha \cdot r_{measured} + (1-\alpha) \cdot r_{old}$) rather than regression.
* **Model 1** uses a **Simple Linear Regression** formulation ($y = mx + c$), which is easy to implement manually with a basic set of equations.
* **Model 3** requires **Multiple Linear Regression** ($y = a \cdot x_1 + b \cdot x_2 + d$), which is complex and better handled by a dedicated library like scikit-learn.

---

### 4. Model Details

**Model 0: Linear EMA**

$$
t = \frac{\Delta T}{\text{rate}_{EMA}}
$$

This model assumes a linear relationship where the building warms up at a specific rate ($^\circ F/\text{min}$). It does not use regression (least squares); instead, it "learns" by averaging yesterday's performance into a running average:

$$
\text{rate}_{EMA,new} = \text{rate}_{EMA,old} + \alpha \cdot (\text{rate}_{observed} - \text{rate}_{EMA,old})
$$

---

**Model 1: Manual Simple Regression**

$$
t = \alpha_{1,a} \cdot (\Delta T^2) + \alpha_{1,b}
$$

In this formula, the duration ($t$) is the dependent variable ($y$), and the squared temperature difference ($\Delta T^2$) is the single independent variable ($x$).

* **Implementation:** Model 1 implements the core tuning logic in `_compute_regression_for_mode` by manually calculating the sums needed for the **ordinary least squares (OLS)** solution.
* **Why Manual?** Simple Linear Regression has basic, closed-form equations (the familiar $\frac{n \Sigma xy - \Sigma x \Sigma y}{n \Sigma x^2 - (\Sigma x)^2}$ formula) that are short and reliable enough to code directly without needing external libraries.

---

**Model 3: Scikit-learn for Multiple Regression**

$$
t = \alpha_{3,a} \cdot \Delta T + \alpha_{3,b} \cdot \Delta T \cdot \text{WF} + \alpha_{3,d}
$$

In this formula, the model has **two distinct features** used for prediction:
1.  **Feature $x_1$:** The temperature difference ($\Delta T$).
2.  **Feature $x_2$:** The weather-compensated term ($\Delta T \cdot \text{WF}$), where $\text{WF} = \frac{T_{sp} - T_{o}}{60.0}$.

This is a classic **Multiple Linear Regression** problem, essentially fitting $y \approx \alpha_{3,a} \cdot x_1 + \alpha_{3,b} \cdot x_2 + \alpha_{3,d}$.

* **Implementation:** Model 3 uses the `sklearn.linear_model.LinearRegression` class in its `_compute_regression_for_mode` method.
* **Why Scikit-learn?** Implementing Multiple Linear Regression requires **matrix algebra** (specifically, solving $\mathbf{w} = (\mathbf{X}^T \mathbf{X})^{-1} \mathbf{X}^T \mathbf{y}$). Using `scikit-learn` handles the necessary matrix computations (like inverting the feature matrix) and ensures better numerical stability and optimization, greatly simplifying the code compared to a manual implementation.

</details>

---

<details>
<summary>🧑‍🏫 30-Day Crash Course: Self-Tuning Algebraic Models & EMA (Optimal Start math refresher)</summary>

Here is a **focused 30-day crash course** designed **specifically for your background** (HVAC, BAS, Niagara, physics, control systems), but aimed at refreshing the **math of self-tuning algebraic models** and **EMA (Exponential Moving Average)** exactly as they appear in PNNL Optimal Start Models 0, 1, and 3.

> Feed into ChatGPT and ask it day by day to make you a new lesson!

This curriculum is **practical**, **Niagara-relevant**, and **hands-on**, with tiny exercises you can do in your head or in a 10-line Python cell.

**Designed for: Niagara Programmer + BAS Controls Engineer + Optimization Developer**

Each day is 10–20 minutes. At the end, you’ll understand PNNL Model 0/1/3 completely from the math side.

---

### WEEK 1 — Foundations of Change, Slopes, and Estimation (Algebra Refresh)

**Day 1 — Δ (delta), rate-of-change, degrees-per-minute**
* Computing $\Delta T$
* Converting $\Delta T/\text{min}$ into a per-minute slope
* Why linear relationships are assumed in HVAC warm-up

**Day 2 — Linear formula refresher: $y = mx + b$**
* $m$ = slope
* $b$ = intercept
* What the slope physically means in HVAC
* Translate $y = mx + b$ to warm-up: $\text{minutes} = a(\Delta T) + b$

**Day 3 — Quadratics refresher: $y = ax^2 + b$**
* Why PNNL Model 1 uses $\Delta T^2$
* Intuition: big temperature deltas warm up disproportionately slower

**Day 4 — Systems of equations refresher**
* Solving two unknowns
* Solving three unknowns
* Use the PNNL Model 3 structure

**Day 5 — Regression without statistics**
* Linear regression as just solving equations
* Why none of this is machine learning
* How least-squares = solving the “best fit” line

**Day 6 — Units, consistency, dimensional analysis**
* Why warm-up models behave badly when units are mixed
* Why WF uses $(T_{set} - T_{oat}) / \alpha$

**Day 7 — Review & interpret sample warm-up data**
* Identify patterns
* When linear vs quadratic vs weather-based model makes sense

---

### WEEK 2 — Exponential Moving Average (EMA) Mastery

**Day 8 — What an EMA actually is (the simplest definition)**

$$
EMA_{new} = EMA_{old} + \alpha (x - EMA_{old})
$$

Why this is perfect for self-tuning BAS models.

**Day 9 — Compute an EMA by hand**
* Use $\alpha = 0.1, 0.3, 0.7$
* Show how smoothing changes with alpha

**Day 10 — How Niagara’s Optimal Start uses EMA**
* `rateDegPerMin` = EMA of observed rate
* `observedRate` = $\Delta T / \text{minutes}$
* How this stabilizes runtime predictions

**Day 11 — EMA vs raw average**
* Why EMA is better for building warm-up
* How EMA eliminates “jumpy” behavior
* Why it self-tunes with each new morning

**Day 12 — EMA as a control loop gain**
* $\alpha$ = the “learning rate”
* $\alpha$ too small → slow learning
* $\alpha$ too large → unstable/erratic predictions

**Day 13 — Double EMA (EMA of EMA)**
* How multi-day smoothing emerges naturally
* Not required in PNNL, but good to know

**Day 14 — Week 2 review**
* Re-do EMA examples
* Re-express them verbally in building control terms

---

### WEEK 3 — Self-Tuning Algebraic Optimal Start Models

**Day 15 — PNNL Model 0 (pure linear EMA model)**

$$
t = \frac{\Delta T}{rate_{EMA}}
$$

How this is literally the simplest self-tuning model in BAS.

**Day 16 — PNNL Model 1 (quadratic algebraic tuning)**

$$
t = a(\Delta T)^2 + b
$$

* How solving two parameters = automatic tuning
* Why fitting curve to real data is self-calibration

**Day 17 — Solve Model 1 by hand**
* 3 datapoints
* Solve $x = \Delta T^2$
* Solve the system
* Update $a, b$

**Day 18 — PNNL Model 3 structure**

$$
t = a (\Delta T) + b (\Delta T \cdot WF) + d
$$

* 3 unknowns
* 3 equations → solvable
* Why WF improves accuracy

**Day 19 — Solve Model 3 coefficients by hand**
Using 3 datapoints and weather factor WF.

**Day 20 — How Niagara stores the coefficients**
* $a$ = “coefficient 1”
* $b$ = “coefficient 2”
* $d$ = “offset”
* $rate_{EMA}$ (Model 0 only)
* Learning happens 1× each morning

**Day 21 — Compare: linear vs quadratic vs weather models**
* When each model is best
* How to visually detect which model fits your site

---

### WEEK 4 — Real-World BAS Application + Coding Fluency

**Day 22 — Building an optimal start dataset**
* What data is needed
* How to clean warm-up data

**Day 23 — Implement Model 0, 1, 3 in basic Python**
* Only add/sub/multiply/divide
* No libraries

**Day 24 — Reinforce solving small linear systems**
* Practice writing and solving 2×2 and 3×3 systems

**Day 25 — Implement full model evaluation logic**
Given: zone start temp, setpoint, OAT, coefficients $a/b/d$. Compute time-to-setpoint.

**Day 26 — Implement self-tuning update logic**
* Append datapoint
* Recompute coefficients
* Replace old coeffs with new ones

**Day 27 — Compare accuracy of the models on fake/historical data**
* Quick sensitivity analysis
* How $\Delta T$ and WF affect predicted minutes

**Day 28 — Identify pathological cases**
* $T_{zone} = T_{setpoint}$
* 0 min actual warmup
* Negative $\Delta T$
* Developer traps in real BAS data

**Day 29 — Build your own hybrid model**
You choose: linear + EMA + weather, or quadratic + EMA.

**Day 30 — Final project: Build a mini-optimal-start engine**
Combine everything from the month:
* Ingest 10 datapoints
* Compute Model 0, 1, 3
* Update them with new run
* Predict tomorrow
* Compare outputs

</details>

---

<details>
<summary>Day 1 — Δ (Delta), Rate-of-Change & Degrees-Per-Minute (DPM)</summary>

**30-Day Crash Course: Self-Tuning Algebraic Models & EMA**
*Day 1 is foundational. No algebra tricks. Just intuition + 3 tiny exercises.*

### 1. What “Δ” Actually Means (BAS + HVAC version)

In HVAC and BAS, **Δ (delta)** simply means: **“How much did something change?”**

In warm-up / optimal start problems:

$$
\Delta T = T_{setpoint} - T_{zone,start}
$$

### 2. Rate of Change (Slope) Refresher

HVAC warm-up is all about **how fast** the temperature rises.

$$
\text{Rate} = \frac{\Delta T}{\Delta t}
$$

**Important:** In optimal start models, the **rate of temperature change** is literally the **degree-per-minute** (DPM) number used in Niagara’s Model 0.

### 3. Why This Matters for Optimal Start

If you know:
* how many degrees you are away from setpoint (**ΔT**)
* how many degrees per minute you can warm up (**rate**)

Then predicted warm-up time is:

$$
t = \frac{\Delta T}{\text{rate}}
$$

This is the **entire foundation** of Model 0 (Linear EMA model).

### 4. Mini-Examples (super quick)

**Example A — Compute ΔT**
Zone = 65°F, Setpoint = 72°F

$$
\Delta T = 72 - 65 = 7^\circ F
$$

**Example B — Compute rate-of-change (DPM)**
Start = 65°F, End = 72°F, Time = 35 minutes

$$
\text{rate} = \frac{7}{35} = 0.20^\circ F/\text{min}
$$

**Example C — Predict warm-up time**
Zone = 68°F, SP = 72°F, Rate = 0.20°F/min

$$
t = \frac{4}{0.20} = 20\ \text{minutes}
$$

</details>

---

<details>
<summary>Day 2 — Linear Formula Refresher: y = m·x + b (HVAC Warm-Up Edition)</summary>

**30-Day Crash Course: Self-Tuning Algebraic Models & EMA**

### 1. What y = m·x + b Really Means (Controls-Friendly Version)

The classic line equation:

$$
y = mx + b
$$

Breaks down into:
* **y** → the output you want (predicted warm-up minutes)
* **x** → the input ($\Delta T$, or sometimes $\Delta T^2$)
* **m** → slope (how sensitive minutes are to $\Delta T$)
* **b** → intercept (baseline warm-up time even when $\Delta T = 0$)

### 2. How it applies to Optimal Start

$$
t = a \cdot \Delta T + b
$$

* **a** = minutes per degree (inverse of DPM)
* **b** = your “dead” time that always occurs no matter what

### 4. Solve a Linear Model by Hand (Easy Example)

Given:
1. $\Delta T = 5^\circ F, \text{Time} = 33 \text{ min}$
2. $\Delta T = 3^\circ F, \text{Time} = 22 \text{ min}$

**Step 1 — Two equations**

$$
\begin{aligned}
33 &= 5m + b \\
22 &= 3m + b
\end{aligned}
$$

**Step 2 — Subtract equations**

$$
(33 - 22) = (5m - 3m) \implies 11 = 2m \implies m = 5.5
$$

**Step 3 — Plug back to find b**

$$
22 = 3(5.5) + b \implies b = 5.5
$$

**Final linear warm-up model:**

$$
t = 5.5(\Delta T) + 5.5
$$

</details>

---

<details>
<summary>Day 3 — Quadratics Refresher: Why Model 1 Uses (ΔT²)</summary>

**30-Day Crash Course: Self-Tuning Algebraic Models & EMA**

### 1. Why Quadratics Show Up in HVAC Warm-Up

A simple linear model ($t = m\Delta T + b$) **underestimates** runtime for large $\Delta T$.

A quadratic:

$$
t = a(\Delta T)^2 + b
$$

**adds curvature** — meaning: “The more $\Delta T$ you have, the more minutes each extra degree costs.” This is exactly what PNNL’s **Model 1** does.

### 4. Solve a Quadratic Model by Hand (Easy HVAC Example)

Suppose you collected 3 warm-up datapoints.
* Note: For Model 1, we often just fit the $x = \Delta T^2$ term.

**Step 1 — Compute $x = \Delta T^2$**
If $\Delta T = 2$, $x = 4$.
If $\Delta T = 4$, $x = 16$.

**Step 2 — Write equations**

$$
\begin{aligned}
10 &= a(4) + b \\
20 &= a(16) + b
\end{aligned}
$$

**Step 3 — Use any two to solve for a and b**
Subtract equations:

$$
10 = 12a \implies a = 0.8333
$$

Plug into eq. 1:

$$
10 = 4(0.8333) + b \implies b = 6.667
$$

Final quadratic warm-up model:

$$
t = 0.8333(\Delta T)^2 + 6.667
$$

</details>

---

<details>
<summary>Day 4 — Systems of Equations Refresher (Foundation of Model 3)</summary>

**30-Day Crash Course: Self-Tuning Algebraic Models & EMA**

### 1. Why Systems of Equations Matter in Optimal Start

In **Model 1**, you solve for **two unknowns**:

$$
t = a(\Delta T)^2 + b
$$

In **Model 3**, you solve for **three unknowns**:

$$
t = a(\Delta T) + b(\Delta T \cdot WF) + d
$$

You need **three equations** (three datapoints) to solve for $a, b, d$.

### 2. Warm-Up Example of a 2×2 System

Given:

$$
\begin{aligned}
16 &= 9a + b \\
30 &= 25a + b
\end{aligned}
$$

Subtract the first equation from the second:

$$
14 = 16a \implies a = 0.875
$$

Then solve for **b**:

$$
16 = 9(0.875) + b \implies b = 8.125
$$

</details>

---

<details>
<summary>Day 5 — Regression Without Statistics (Just Algebra)</summary>

**30-Day Crash Course: Self-Tuning Algebraic Models & EMA**

### 1. Why regression ≠ statistics in optimal start

In the context of HVAC optimal start, regression is simply: **“Solve for the coefficients that best fit your warm-up data.”**

**For Model 1:**
$$
t = ax + b \quad (\text{where } x = \Delta T^2)
$$

**For Model 3:**
$$
t = ax_1 + bx_2 + d \quad (\text{where } x_1 = \Delta T, x_2 = \Delta T \cdot WF)
$$

### 4. A Clean Example of Algebraic Regression

You have two warmed-up datapoints:
1. $x = 9, t = 14$
2. $x = 49, t = 50$

**Step 1 — Compute slope (a)**

$$
a = \frac{50 - 14}{49 - 9} = \frac{36}{40} = 0.9
$$

**Step 2 — Solve for intercept (b)**

$$
14 = 9(0.9) + b \implies b = 5.9
$$

**Final regression model:**

$$
t = 0.9x + 5.9
$$

</details>

---

<details>
<summary>Day 6 — What “Self-Tuning” Really Means</summary>

**30-Day Crash Course: Self-Tuning Algebraic Models & EMA**

### 2. Two Flavors of Self-Tuning

**Type 1 — Self-tuning with EMA (Model 0)**
This handles **single-slope** models.

$$
\text{newRate} = \alpha \cdot \text{measuredRate} + (1 - \alpha) \cdot \text{oldRate}
$$

**Type 2 — Self-tuning via Algebraic Regression (Model 1, Model 3)**
This handles models with **coefficients** ($a, b, d$). Every morning, you compute the new coefficients based on the new run, then blend them:

$$
a_{\text{new}} = 0.85 a_{\text{old}} + 0.15 a_{\text{today}}
$$

### 3. Self-Tuning Example — Linear EMA (Model 0)

Yesterday’s Rate = 0.20. Today's measured Rate = 0.15. $\alpha = 0.10$.

$$
\text{newRate} = 0.10(0.15) + 0.90(0.20) = 0.015 + 0.18 = 0.195
$$

New slope nudges downward — building is slower. This is **self-tuning in one line of Python**.

</details>

---


<details>
<summary>Day 7 </summary>


</details>

---


<details>
<summary>Day 8 </summary>


</details>

---


<details>
<summary>Day 9 </summary>


</details>

---


<details>
<summary>Day 10 </summary>


</details>

---


<details>
<summary>Day 11 </summary>


</details>

---


<details>
<summary>Day 12 </summary>


</details>

---


<details>
<summary>Day 13 </summary>


</details>

---


<details>
<summary>Day 14 </summary>


</details>

---


<details>
<summary>Day 15 </summary>


</details>

---


<details>
<summary>Day 16 </summary>


</details>

---


<details>
<summary>Day 17 </summary>


</details>

---


<details>
<summary>Day 18 </summary>


</details>

---


<details>
<summary>Day 19 </summary>


</details>

---


<details>
<summary>Day 20 </summary>


</details>

---


<details>
<summary>Day 21 </summary>


</details>

---


<details>
<summary>Day 22 </summary>


</details>

---


<details>
<summary>Day 23 </summary>


</details>

---


<details>
<summary>Day 24 </summary>


</details>

---


<details>
<summary>Day 25 </summary>


</details>

---


<details>
<summary>Day 26 </summary>


</details>

---


<details>
<summary>Day 27 </summary>


</details>

---


<details>
<summary>Day 28 </summary>


</details>

---


<details>
<summary>Day 29 </summary>


</details>

---


<details>
<summary>Day 30 </summary>


</details>