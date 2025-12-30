# hvac-optimal-start-math-playground

This repo teaches **HVAC optimal-start mathematics** and provides a **Python learning playground** for exploring algebraic models, regression techniques, and self-tuning methods. It is intentionally written for **BAS technicians with a basic algebra background**, not necessarily for advanced academic audiences such as PhD-level engineers—**but anyone is welcome to learn, contribute, and get involved!**

All optimal-start models share one goal: predicting the `minutes` needed for a zone to reach setpoint before occupancy. When properly tuned, this becomes a powerful energy-savings strategy.

```text
[ Zone Temp, Setpoint, Schedule ]  --->  { OPTIMAL-START MATH MODEL }  --->  Minutes to Warm/Cool
```

This repository dives deeply into **how each mathematical model transforms these inputs into a time prediction**, and why the math matters for real BAS performance. The assumption that learner already understand HVAC physics and system behavior at a high level, the lesson plans require only intermediate math — roughly high-school–level advanced algebra — plus beginner-level Python (basic syntax and math operators). 

The project standardizes the **inputs, outputs, and mathematical structures** used across all models described in the PNNL publication (see the
[pdf directory](https://github.com/bbartling/hvac-optimal-start-math-playground/tree/develop/PNNL_Paper)).
Model 0 is included as a **traditional linear degrees-per-minute (DPM)** approach found in many BAS platforms, even though it is *not* part of the PNNL paper.

---

## 📝 Model Summary — The Plain-English Version

| Model | What It Does (Plain English) |
| :--- | :--- |
| **Model 0 — Linear (Tridium kitControl)** | Assumes the building warms at a **constant rate** (e.g., 0.5°F per minute). This is the standard logic found inside the default Tridium Niagara `kitControl` optimal start block. Simple, stable, and widely used. |
| **Model 1 — Quadratic (Curved Relationship)** | Models warm-up time as increasing **non-linearly** as ΔT grows. Useful when large deltas take disproportionately longer than small deltas — a very common real-world behavior. |
| **Model 2 — Linear + Weather Bump** | Same as Model 0 but adds a small correction when today's weather is colder than reference conditions. Rarely used; mathematically limited, but included for completeness. |
| **Model 3 — Weather-Enhanced Linear Model** | Models warm-up as a combination of **ΔT** *and* a **weather factor (WF)**. Much more expressive than Model 2. Handles weather swings well and is the most general-purpose model. |
| **Model 4 — Saturation / Coasting Model** | Models situations where heating slows down as it nears setpoint. Useful when the last few degrees take disproportionately longer (coil approach, stratification, low airflow, etc.). |
| **Model 5 — Gradient Descent (Future Research)** | For learning purposes, a custom Machine Learning engine built from scratch. Instead of using algebra, it "learns" weights for complex features (like the "Monday Morning" cold soak) by iteratively minimizing error over thousands of training epochs. |

---

## Model Overview

### Model 0 — Linear Rate Model (EMA-Based)
Model 0 estimates warm-up or cool-down time using a smoothed rate of temperature
change:

```
minutes = ΔT / rate
```

The rate is updated using an **Exponential Moving Average (EMA)**, making Model 0
inherently self-tuning and stable.

> ✅ EMA is explicitly part of Model 0 behavior.

---

### Model 1 — Quadratic-in-ΔT Model
Model 1 captures non-linear behavior between temperature difference and run time:

```
t = α₁,a · (ΔT²) + α₁,b
```

Coefficients are learned via **ordinary least squares (OLS)** regression using
historical run data.

#### 🔎 Implementation Note (Not in the PNNL Paper)

The original PNNL paper recomputes Model 1 coefficients using a rolling historical
window (e.g., the last N days).

In this repository, an **optional EMA smoothing layer** is applied to the learned
coefficients (α₁,a and α₁,b):

```
α_est ← α_prev + λ · (α_new − α_prev)
```

This enhancement:
- Reduces day-to-day jitter
- Improves numerical stability
- Makes the model safer for noisy or sparse BAS data

> ⚠️ EMA smoothing for Model 1 is a **practical field enhancement**, not a
> requirement of the original PNNL formulation.

---

### **Model 3 — Multi-Factor Weather-Compensated Model**

Model 3 blends **indoor temperature**, **outdoor air temperature**, and **historical learning** to estimate optimal start time.
It extends Model 1 by explicitly accounting for the interaction between indoor temperature deficit and outdoor conditions.

The model predicts start time as:

$$
t_{\text{pred}} = a_1(\Delta T) + a_2(\Delta T)(T_z - T_o) + a_3
$$

where:

* $\Delta T = (T_{\text{setpoint}} - T_{\text{zone,current}})$
* $T_o$ is outdoor air temperature
* $(a_1, a_2, a_3)$ are continuously self-tuned parameters learned from past day performance

Meaning:

* Larger zone deficit → longer start time
* Greater difference between zone temperature and outdoor temperature → adjusts runtime based on weather exposure
* The algorithm **self-biases** each day based on how accurate yesterday’s prediction was

This model is best for zones where both:

* Thermal mass matters, **and**
* Outdoor temperature strongly influences warm-up / cool-down behavior

---

### **Model 4 — First-Order Response / Physics-Driven Model**

Model 4 uses a **first-order thermal response model** derived from building physics instead of pure curve-fit regression.

It assumes the zone behaves like a **first-order system** and estimates the time needed to reach setpoint based on how temperature actually responds after unit startup.

Optimal start time is computed using:

$$
t_{\text{pred}} =
\frac{\ln\left(\frac{\alpha_{a}}{\alpha_{b}}\right)}
{\ln(\alpha_{c})}
$$

where:

* $\alpha_a$ – acceptable temperature tolerance band (deadband)
* $\alpha_b$ – **initial temperature difference** between zone and setpoint
* $\alpha_c$ – **dynamic system response factor**, continuously updated using least-squares learning from historical recovery curves

Interpretation:

* **Larger initial temperature gap → longer runtime**
* **Stronger system response → shorter runtime**
* Updates continuously as equipment and weather change

Model 4 is powerful because it:

* Adapts automatically to aging equipment
* Learns real thermal behavior
* Handles changing load patterns
* Requires less hand-tuning than pure regression

---

### **Model 5 — Machine Learning**

* TODO 


---

## 🧑‍🏫 50-Day Crash Course: Master All 5 Models + The "Monday Problem"

> **Note:** This expanded course dedicates a full week to each PNNL model. Perfect for BAS professionals who want to master the math one step at a time.

### 👉 **[See Daily Lesson Details](README_LESSON_DETAILS.md)**

Upload this text into your AI assistant to act as your daily math coach.

---

### WEEK 1 — Foundations & Model 0 (The "Cruise Control")
*Focus: Rate of Change & Basic Smoothing*

**Day 1 — The Basics: ΔT and Rate**
* Calculating $\Delta T = T_{setpoint} - T_{zone}$.
* Calculating Rate ($^\circ F/\text{min}$).
* Why simple buildings behave like simple lines.

**Day 2 — The Formula: $t = \Delta T / \text{rate}$**
* The raw math of Model 0.
* Predicting runtime if you know the speed.

**Day 3 — The Noise Problem**
* Why using *only* today's rate is dangerous (jittery control).
* Why we need to look at history.

**Day 4 — Intro to Exponential Moving Average (EMA)**
* What is an EMA? (The "smoothing" filter).
* The formula: $EMA_{new} = EMA_{old} + \alpha(Current - EMA_{old})$.

**Day 5 — Tuning the Alpha ($\alpha$)**
* What happens if $\alpha = 0.1$ (Slow) vs $\alpha = 0.9$ (Fast).
* Picking the right "learning speed" for HVAC.

**Day 6 — Simulating Model 0 (Paper & Pencil)**
* Take 3 days of fake data.
* Update the rate manually.
* See the self-tuning happen on paper.

**Day 7 — Week 1 Review: The Limits of Linear**
* Where Model 0 fails (Extreme weather, deep setbacks).
* Why we need curves.

---

### WEEK 2 — Model 1: The "Heavy Lifter" (Quadratic)
*Focus: The Physics of Thermal Mass*

**Day 8 — Why Heat Transfer isn't Linear**
* Why the last degree takes longer than the first degree.
* Intro to the Quadratic Curve: $t = a(\Delta T)^2 + b$.

**Day 9 — The "Dead Time" Intercept ($b$)**
* Why units run for 10 minutes before the temp sensor even moves.
* Accounting for sensor lag and duct warmup.

**Day 10 — The Slope Coefficient ($a$)**
* This represents the "heaviness" of the zone.
* Higher $a$ = Slower warm up.

**Day 11 — Simple Regression (Line Fitting)**
* How to draw the "best fit" line through messy data points.
* We don't need AI; we just need algebra.

**Day 12 — Solving for $a$ and $b$ (Manual Math)**
* Using the sum of squares.
* The standard OLS (Ordinary Least Squares) formulas.

**Day 13 — Self-Tuning Model 1**
* Applying EMA to coefficients $a$ and $b$.
* How the curve gently shifts as the season changes.

**Day 14 — Week 2 Review: Model 0 vs. Model 1**
* Compare predictions on a "Deep Setback" day.
* Why Model 1 is usually safer for interior zones.

---

### WEEK 3 — Model 2: The "Weather Watcher" (Ratio Adjustment)
*Focus: Simple Outdoor Air Compensation*

**Day 15 — Why Indoor Temp isn't enough**
* Perimeter zones lose heat *while* they are trying to warm up.
* Introduction to Model 2.

**Day 16 — The Reference Temperature ($T_{ref}$)**
* Choosing a baseline (e.g., $0^\circ F$ for heating, $100^\circ F$ for cooling).
* Why we need a "worst case" anchor point.

**Day 17 — The Ratio Formula**
* Math: $\text{Ratio} = (T_{ref} - T_{oat,yesterday}) / (T_{ref} - T_{oat,today})$.
* How this ratio stretches or shrinks the runtime.

**Day 18 — Calculating the Base Rate ($\alpha_{2,a}$)**
* Similar to Model 0, but calculated *before* the weather adjustment.

**Day 19 — The "Double Prediction"**
* Step 1: Predict time based on indoor temp.
* Step 2: Multiply by the weather ratio.

**Day 20 — Sensitivity Check**
* What happens if today is $10^\circ$ colder than yesterday?
* Does the model overreact?

**Day 21 — Week 3 Review: Perimeter vs. Core**
* When to use Model 2 (Windows/Exterior) vs Model 1 (Core).

---

### WEEK 4 — Model 3: The "Smart Brain" (Multiple Regression)
*Focus: Matrix Math & Advanced logic*

**Day 22 — The Missing Link: Weather Factor (WF)**
* Calculating $WF = (T_{sp} - T_{oat}) / 60$.
* Normalizing the outdoor influence.

**Day 23 — The Big Equation**
* $t = a \cdot \Delta T + b \cdot (\Delta T \cdot WF) + d$.
* Understanding the three moving parts.

**Day 24 — Multiple Regression Concept**
* We are no longer fitting a line; we are fitting a 3D plane.
* Why we can't easily solve this with pencil and paper.

**Day 25 — Intro to Matrices (For Technicians)**
* What is a Matrix? (Just a spreadsheet grid of numbers).
* How Python uses matrices to solve the equation instantly.

**Day 26 — Handling "Weird" Coefficients**
* What if the math says $b$ is negative? (Does colder weather make it heat *faster*?)
* Why we clamp values to 0.

**Day 27 — Tuning Model 3**
* How much history do you need? (PNNL suggests 10 days).
* The danger of "overfitting" on short data.

**Day 28 — Week 4 Review: Is it worth it?**
* Comparing Model 1 accuracy vs. Model 3 complexity.
* When is "Simple" better than "Smart"?

---

### WEEK 5 — Model 4: The "Physicist" (Logarithmic Decay)
*Focus: Time Constants & Exponential Decay*

**Day 29 — Thinking like a Capacitor**
* How buildings charge and discharge heat like a battery.
* Introduction to the Time Constant ($\tau$).

**Day 30 — The Logarithm ($\ln$)**
* Why we use natural logs in HVAC.
* The formula: $t = \ln(\text{Deadband} / \Delta T) / \ln(\text{DecayRate})$.

**Day 31 — Calculating the Decay Rate ($\alpha_c$)**
* Looking at how fast the error dropped yesterday.
* It's a measure of "system power" vs "load".

**Day 32 — The "Coast to Stop" effect**
* Model 4 is great for systems that slow down as they get closer to setpoint.
* Why this prevents overshooting.

**Day 33 — Comparing Log vs. Quadratic**
* Graphing Model 1 vs Model 4.
* Which one fits *your* building better?

**Day 34 — Coding Model 4**
* Using the `math.log()` function in Python/Java.
* Handling "Divide by Zero" errors in logs.

**Day 35 — Week 5 Review: The Full Arsenal**
* You now know Linear, Quadratic, Ratio, Regression, and Logarithmic models.
* You are a math wizard. 🧙‍♂️

---

### WEEK 6 — The "Monday Morning" Boss Battle
*Focus: Real World Problems & Hybrid Logic*

**Day 36 — The "Monday Morning" Problem Defined**
* [cite_start]**The Issue:** PNNL proved all models fail on Mondays.
* **The Cause:** Building mass "cold soaks" over the weekend. 48 hours off is different than 12 hours off.

**Day 37 — Why Math Fails Here**
* Models rely on *recent* history (Tuesday–Friday).
* Monday behaves like a distinct, separate system.

**Day 38 — The "Technician's Guess"**
* The industry standard: "Just add 60 minutes to the start time on Monday."
* Is it crude? Yes. Does it work? Usually.

**Day 39 — Experiment: The "Weekend Factor"**
* Instead of a fixed hour, multiply the Model 3 prediction by 1.2 or 1.3.
* Drafting logic for a "Cold Soak Multiplier."

**Day 40 — Experiment: Separate Histories**
* Idea: Keep a separate database just for Mondays.
* Pros/Cons: It takes 10 weeks to get 10 data points!

**Day 41 — Designing the Ultimate Hybrid**
* Logic:
    * IF $\Delta T < 2^\circ$: Use **Model 0** (Simple).
    * IF $\Delta T > 2^\circ$ AND Not Monday: Use **Model 3** (Smart).
    * IF Monday: Use **Model 3** + **Technician Adder** (Safe).

**Day 42 — Final Project: The Monday Showdown**
* Take 5 real "Monday" datapoints.
* Calculate Model 3 prediction.
* Calculate "Technician" prediction (+60 mins).
* Compare to actual runtime.
* **Verdict:** Did the math beat the gut instinct?

---

### WEEK 7 — The Future: Building an AI Engine from Scratch
*Focus: Gradient Descent, Normalization, & Custom Weights*

**Day 43 — Algebra vs. Iteration**
* The difference between "solving" (Algebra) and "guessing" (Machine Learning).
* The "Hot or Cold" game: How computers find answers without formulas.

**Day 44 — The Cost Function (MSE)**
* Quantifying "Wrongness."
* Why we square the error (punishing big mistakes).
* The goal: Make this one number zero.

**Day 45 — The Gradient (The "Nudge")**
* Standing on a mountain in the fog.
* How the error tells us which direction to step.
* Calculating the slope: $\text{Gradient} = \text{Error} \times \text{Input}$.

**Day 46 — The Learning Rate ($\eta$)**
* The "Throttle" of your AI engine.
* The Update Rule: $\text{Weight}_{new} = \text{Weight}_{old} - (\text{Rate} \times \text{Gradient})$.
* What happens if you learn too fast (Explosion) vs. too slow (Stall).

**Day 47 — Feature Engineering (Data Prep)**
* Why math hates big numbers (Normalization).
* **One-Hot Encoding:** Converting "Monday" into `1.0` and `0.0`.
* Creating the Input Vector: `[Scaled_DeltaT, Is_Monday]`.

**Day 48 — The Epoch Loop**
* What is an Epoch? (Seeing the whole history once).
* Writing the training loop that runs 2,000 times.
* Watching the Loss curve drop.

**Day 49 — The "Monday Neuron" (Interpreting Weights)**
* Reading the mind of the machine.
* If Weight #2 is `45.0`, the AI *learned* that Mondays need 45 extra minutes.
* No IF statements, just math.

**Day 50 — The Final Boss: Full Custom Engine**
* Build "Model 5" from scratch using only `numpy`.
* Train it on 20 days of data (including cold Mondays).
* **Victory:** Watch it automatically predict longer runtimes for Monday without being told to.

---

### 👉 **See Also For Niagara Building Automation**

You can also find **active Java implementations for Niagara 4** in the Vibe Coder
[repository](https://github.com/bbartling/niagara4-vibe-code-addict/blob/develop/README_OPT_START.md),
where Models 0 and 1 are currently being field-tested on real `ProgramObject`s.

Because Niagara `ProgramObject`s are not well-suited for manual matrix algebra, **Model 3 (multiple regression)** is omitted from the Niagara implementation — but **fully supported in Python**, where regression and matrix operations are trivial to perform.

---

## 📜 License

Everything here is **MIT Licensed** — free, open source, and made for the BAS community.  
Use it, remix it, or improve it — just share it forward so others can benefit too. 🥰🌍


【MIT License】

Copyright 2025 Ben Bartling

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.