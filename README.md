# hvac-optimal-start-math-playground

This repo teaches HVAC optimal-start math + contains Python learning playground material.

This reference outlines the consistent inputs and outputs used across `OptimalStartModel1` and `OptimalStartModel3` based on the PNNL paper in the [pdf](https://github.com/bbartling/hvac-optimal-start-math-playground/tree/develop/PNNL_Paper) directory.


Also see the active Java implementations in the Vibe Coder
[repository](https://github.com/bbartling/niagara4-vibe-code-addict/blob/develop/README_OPT_START.md).
These versions are currently being tested by Ben in the field on a Niagara 4 `ProgramObject` for Models 0 and 1.

Because a `ProgramObject` has practical limitations, **Model 3 (Multiple Regression)** is omitted from the Niagara implementation to avoid doing complex matrix algebra by hand.
However, **Model 3 is fully supported in Python**, where math libraries make regression and matrix operations straightforward.


---

## 📝 Model Summary (The "Plain English" Version)

We use different math models because different zones behave differently. Here is the cheat sheet for which model does what.

| Model | The Logic (Plain English) | Best Application |
| :--- | :--- | :--- |
| **Model 0** | **The "Cruise Control"**<br>It assumes your unit heats up at a constant speed (e.g., 0.5°F per minute). It simply averages yesterday's speed to guess today's. | **General Use**<br>Great for mild climates or simple RTUs where precision isn't critical. |
| **Model 1** | **The "Heavy Lifter"**<br>It knows that heating up a cold room gets harder the longer it runs. [cite_start]It uses a curved line (quadratic) instead of a straight one. [cite: 236, 237] | [cite_start]**Interior Zones**<br>Best for zones with thick walls (high thermal mass) that ignore the weather outside. [cite: 237] |
| **Model 2** | **The "Weather Watcher"**<br>Like Model 0, but it checks if it's colder outside than yesterday. [cite_start]If it's colder, it adds extra runtime automatically. [cite: 221, 223] | [cite_start]**Perimeter Zones**<br>Best for zones with windows or thin walls that feel the outdoor temperature immediately. [cite: 223] |
| **Model 3** | **The "Smart Brain"**<br>The most accurate model. [cite_start]It looks at *both* how cold the room is AND how cold it is outside to calculate the perfect start time. [cite: 252] | [cite_start]**High Performance**<br>Best for maximum energy savings on complex zones where OAT swings matter a lot. [cite: 1688] |
| **Model 4** | [cite_start]**The "Coaster"**<br>It assumes the temperature change slows down as it gets closer to the setpoint (like a car coasting to a stop). [cite: 270, 271] | **Fast Systems**<br>Good for systems that heat up fast initially but struggle to squeeze out the last few degrees. |

### 🛠️ How hard are they to program?

* **Model 0 (Easy):** Just simple division. Any BAS controller can do this easily.
* **Model 1 & 2 (Medium):** Requires basic algebra. You can do this in most PLCs or Niagara Program objects.
* **Model 3 (Hard):** Requires "Matrix Algebra." This is very hard to code from scratch in a standard BAS controller. It is best suited for Python or edge devices that have math libraries.
* **Model 4 (Medium/Hard):** Uses logarithms (ln). Requires a controller that supports advanced math functions.

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

**Python Implementation:**
```python
# 1. Calculate observed rate from today's run
observed_rate = delta_t / actual_minutes

# 2. Update EMA (Learn)
# alpha is typically 0.1 to 0.3
rate_ema = rate_ema + alpha * (observed_rate - rate_ema)
```

### Model 1: Manual Simple Regression

$$
t = \alpha_{1,a} \cdot (\Delta T^2) + \alpha_{1,b}
$$

In this formula, the duration ($t$) is the dependent variable ($y$), and the squared temperature difference ($\Delta T^2$) is the single independent variable ($x$).

  * **Implementation:** Model 1 implements the core tuning logic in `_compute_regression_for_mode` by manually calculating the sums needed for the **ordinary least squares (OLS)** solution.
  * **Why Manual?** Simple Linear Regression has basic, closed-form equations (the familiar $\frac{n \Sigma xy - \Sigma x \Sigma y}{n \Sigma x^2 - (\Sigma x)^2}$ formula) that are short and reliable enough to code directly without needing external libraries.

**Python Implementation:**

```python
# x = deltaT^2, y = actual_minutes
n = len(xs)
sum_x = sum(xs)
sum_y = sum(ys)
sum_xy = sum(x*y for x, y in zip(xs, ys))
sum_x2 = sum(x*x for x in xs)

# Solve for slope (a) and intercept (b) manually
a = (n*sum_xy - sum_x*sum_y) / (n*sum_x2 - sum_x**2)
b = (sum_y - a*sum_x) / n
```

### Model 2: Weather-Adjusted Rate

$$
t_{opt} = \frac{(T_{sp} - T_{z,0})}{\alpha_{2,a}} \cdot \left( \frac{T_{o,r} - T_{o,prev}}{T_{o,r} - T_{o,curr}} \right)
$$

This model adds an **outdoor air temperature adjustment** to the simple linear rate. It compares today's outdoor temperature ($T_{o,curr}$) to yesterday's ($T_{o,prev}$) relative to a reference temperature ($T_{o,r}$, typically $0^\circ C$ for heating or $100^\circ F$ for cooling).

  * $\alpha_{2,a}$: The learned rate of temperature change (similar to Model 0).
  * [cite_start]**Adjustment Factor:** If it is colder today than yesterday, the ratio increases, extending the predicted start time[cite: 161].

**Python Implementation:**

```python
# 1. Learn the base rate (alpha_2a) from yesterday
# rate = delta_T / minutes
alpha_2a = (setpoint - zone_start_prev) / actual_minutes_prev

# 2. Predict today using outdoor temp correction
# T_ref = 0 (heating) or 100 (cooling)
correction = (T_ref - oat_prev) / (T_ref - oat_curr)
predicted_minutes = ((setpoint - zone_start_curr) / alpha_2a) * correction
```

### Model 3: Scikit-learn for Multiple Regression

$$
t = \alpha_{3,a} \cdot \Delta T + \alpha_{3,b} \cdot \Delta T \cdot \text{WF} + \alpha_{3,d}
$$

In this formula, the model has **two distinct features** used for prediction:

1.  **Feature $x_1$:** The temperature difference ($\Delta T$).
2.  **Feature $x_2$:** The weather-compensated term ($\Delta T \cdot \text{WF}$), where $\text{WF} = \frac{T_{sp} - T_{o}}{60.0}$.

This is a classic **Multiple Linear Regression** problem, essentially fitting $y \approx \alpha_{3,a} \cdot x_1 + \alpha_{3,b} \cdot x_2 + \alpha_{3,d}$.

  * **Implementation:** Model 3 uses the `sklearn.linear_model.LinearRegression` class in its `_compute_regression_for_mode` method.
  * **Why Scikit-learn?** Implementing Multiple Linear Regression requires **matrix algebra** (specifically, solving $\mathbf{w} = (\mathbf{X}^T \mathbf{X})^{-1} \mathbf{X}^T \mathbf{y}$). Using `scikit-learn` handles the necessary matrix computations (like inverting the feature matrix) and ensures better numerical stability and optimization.

**Python Implementation (Matrix Math):**

```python
import numpy as np
from sklearn.linear_model import LinearRegression

# X = [[deltaT, deltaT * WF], ...]
# y = [minutes, ...]

model = LinearRegression()
model.fit(X, y)

a = model.coef_[0]
b = model.coef_[1]
d = model.intercept_
```

### Model 4: First-Order Response (Logarithmic)

$$
t = \frac{\ln(\alpha_{4,a} / \alpha_{4,b})}{\ln(\alpha_{4,c})}
$$

This model assumes the zone temperature behaves like a **first-order differential equation** (exponential decay towards setpoint). [cite_start]It fits the "decay rate" ($\alpha_{4,c}$) based on how quickly the error ($T_{sp} - T_z$) reduced during the previous run[cite: 271, 317].

  * $\alpha_{4,a}$: The acceptable temperature deadband (e.g., $0.5^\circ F$).
  * $\alpha_{4,b}$: The initial temperature difference ($T_{sp} - T_{z,0}$).
  * $\alpha_{4,c}$: The learned system time constant/decay factor.

**Python Implementation:**

```python
import math

# 1. Estimate decay factor (alpha_c) from history
# This is simplified; usually requires least-squares on the error log
error_ratio_sum = sum(error_t / error_t_minus_1 for error in history)
alpha_c = error_ratio_sum / len(history)

# 2. Predict time
# alpha_a = deadband (e.g., 0.5)
# alpha_b = current delta T
numerator = math.log(alpha_a / current_delta_t)
denominator = math.log(alpha_c)

predicted_minutes = numerator / denominator
```

---

## 🧑‍🏫 42-Day Crash Course: Master All 5 Models + The "Monday Problem"

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
* [cite_start]**The Issue:** PNNL proved all models fail on Mondays[cite: 27, 28].
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



## 📜 License

Everything here is **MIT Licensed** — free, open source, and made for the BAS community.  
Use it, remix it, or improve it — just share it forward so others can benefit too. 🥰🌍


【MIT License】

Copyright 2025 Ben Bartling

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.