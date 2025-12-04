# hvac-optimal-start-math-playground

This repo teaches HVAC optimal-start math + contains Python learning playground material.

This reference outlines the consistent inputs and outputs used across `OptimalStartModel1` and `OptimalStartModel3` based on the PNNL paper in the [pdf](https://github.com/bbartling/niagara4-vibe-code-addict/tree/develop/pdf) directory.

Also see active Java versions on the vibe coder [repository](https://github.com/bbartling/niagara4-vibe-code-addict/blob/develop/README_OPT_START.md) which is actively being tested by Ben in the field in the Niagara4 framework in a `ProgramObject`.

---

## 📝 Model Equations Summary

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

## 4. Model Details

### Model 0: Linear EMA

$$
t = \frac{\Delta T}{\text{rate}_{EMA}}
$$

This model assumes a linear relationship where the building warms up at a specific rate ($^\circ F/\text{min}$). It does not use regression (least squares); instead, it "learns" by averaging yesterday's performance into a running average:

$$
\text{rate}_{EMA,new} = \text{rate}_{EMA,old} + \alpha \cdot (\text{rate}_{observed} - \text{rate}_{EMA,old})
$$

### Model 1: Manual Simple Regression

$$
t = \alpha_{1,a} \cdot (\Delta T^2) + \alpha_{1,b}
$$

In this formula, the duration ($t$) is the dependent variable ($y$), and the squared temperature difference ($\Delta T^2$) is the single independent variable ($x$).

* **Implementation:** Model 1 implements the core tuning logic in `_compute_regression_for_mode` by manually calculating the sums needed for the **ordinary least squares (OLS)** solution.
* **Why Manual?** Simple Linear Regression has basic, closed-form equations (the familiar $\frac{n \Sigma xy - \Sigma x \Sigma y}{n \Sigma x^2 - (\Sigma x)^2}$ formula) that are short and reliable enough to code directly without needing external libraries.

### Model 3: Scikit-learn for Multiple Regression

$$
t = \alpha_{3,a} \cdot \Delta T + \alpha_{3,b} \cdot \Delta T \cdot \text{WF} + \alpha_{3,d}
$$

In this formula, the model has **two distinct features** used for prediction:
1.  **Feature $x_1$:** The temperature difference ($\Delta T$).
2.  **Feature $x_2$:** The weather-compensated term ($\Delta T \cdot \text{WF}$), where $\text{WF} = \frac{T_{sp} - T_{o}}{60.0}$.

This is a classic **Multiple Linear Regression** problem, essentially fitting $y \approx \alpha_{3,a} \cdot x_1 + \alpha_{3,b} \cdot x_2 + \alpha_{3,d}$.

* **Implementation:** Model 3 uses the `sklearn.linear_model.LinearRegression` class in its `_compute_regression_for_mode` method.
* **Why Scikit-learn?** Implementing Multiple Linear Regression requires **matrix algebra** (specifically, solving $\mathbf{w} = (\mathbf{X}^T \mathbf{X})^{-1} \mathbf{X}^T \mathbf{y}$). Using `scikit-learn` handles the necessary matrix computations (like inverting the feature matrix) and ensures better numerical stability and optimization, greatly simplifying the code compared to a manual implementation.

---

## 🧑‍🏫 30-Day Crash Course: Self-Tuning Algebraic Models & EMA

> **Note:** This course is designed for BAS/HVAC professionals. Each lesson takes 10–20 minutes.

### WEEK 1 — Foundations of Change, Slopes, and Estimation

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

### 👉 **[See Daily Lesson Details](README_LESSON_DETAILS.md)**

Your personal day-by-day companion for this 30-day crash course.

Upload it into your favorite AI assistant and let it **coach you**, **clarify concepts**, and **walk you through the math** — *not to cheat*, but to accelerate your understanding of these advanced HVAC optimization techniques.

Every concept you learn here contributes directly to:

🌡️ **Reducing HVAC runtime**
⚡ **Cutting energy waste**
🏢 **Smoother building operation**
🌎 **A healthier planet and environment**

This is the same math behind high-performance BAS systems, Optimal Start models, and real-world energy savings.
Use it, experiment with it, modify it — **become dangerous with it** 😀😊😂🤣.


---

## 📜 License

Everything here is **MIT Licensed** — free, open source, and made for the BAS community.  
Use it, remix it, or improve it — just share it forward so others can benefit too. 🥰🌍


【MIT License】

Copyright 2025 Ben Bartling

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.