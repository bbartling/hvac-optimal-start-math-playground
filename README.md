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

## Mathematical Models


### **Model 0 — Adaptive Linear Recovery (EMA-Smoothed)**

Model 0 assumes the zone recovers at an approximately linear rate
(measured in **degrees per minute**). After each completed run, a new rate
measurement is computed:

$$
r_{\text{new}} = \frac{\left|T_{\text{zone,start}} - T_{\text{setpoint}}\right|}{t_{\text{actual}}}
$$

To avoid noisy predictions and allow the system to “learn” over time,
the recovery rate is updated using an **Exponential Moving Average** (EMA):

$$
r_{\text{EMA}}(k) = \alpha \cdot r_{\text{new}} + (1-\alpha)\cdot r_{\text{EMA}}(k-1)
$$

where:

* $\alpha$ is the learning weight (tunable)
* larger $\alpha$ → faster learning
* smaller $\alpha$ → more stability

The predicted optimal start time is then:

$$
t_{\text{pred}} = \frac{\left|T_{\text{zone,current}} - T_{\text{setpoint}}\right|}{r_{\text{EMA}}}
$$

---

### **Model 1 — Quadratic Recovery Model (Interior / Stable Zones)**

For thermally stable or interior zones, recovery behavior often follows
a **non-linear** curve. PNNL recommends fitting a quadratic model of the form:

$$
t = a\cdot(\Delta T)^2 + b\cdot(\Delta T) + c
$$

where:

* * $t = a(\Delta T)^2 + b(\Delta T) + c$
* (a, b, c) are continuously self-tuned regression coefficients
  learned from historical runs.

Thus, optimal start time becomes:

$$
t_{\text{pred}} = a\cdot(\Delta T)^2 + b\cdot(\Delta T) + c
$$

This model works best when outdoor temperature has **minimal influence**
on warm-up or cool-down behavior.

---

### **Model 2 — Weather-Sensitive Linear Model (Exterior / OAT-Driven Zones)**

For exterior or weather-exposed zones, recovery rate changes
significantly with outdoor air temperature (OAT).
Model 2 begins with a baseline Model-0 prediction:

$$
t_{\text{base}} = \frac{\left|T_{\text{zone,current}} - T_{\text{setpoint}}\right|}{r_{\text{EMA}}}
$$

Then applies a learned **OAT sensitivity ratio**:

$$
t_{\text{pred}} = t_{\text{base}} \cdot R(T_{\text{OAT}})
$$

Where the ratio function is self-tuned over time, commonly modeled as:

$$
R(T_{\text{OAT}}) = m\cdot T_{\text{OAT}} + b
$$

meaning:

* colder weather → longer recovery
* hotter weather → shorter (cooling) or longer (heating), depending on mode
* automatically adapts based on historical runtime error

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

### **Model Selection Logic**

At runtime, models are continuously evaluated and compared based on
historical prediction error:

$$
\text{Error} = t_{\text{pred}} - t_{\text{actual}}
$$

and the system dynamically favors whichever model shows superior accuracy
over recent runs.


---


> So far Model 4 is:

* Has **input data** (ΔT, maybe OAT context indirectly)
* Has **observed outputs** (actual warm-up minutes)
* Has a **model shape**
  ( t = \tau \ln(1 + k\Delta T) )
* Has **fit parameters** (τ, k) so the model best matches reality
* Has evaluate error and re-train when new runs happen

That is formally:

### 👉 **Nonlinear Regression**

which lives under the umbrella of **supervised machine learning**.

Linear regression → ML
Quadratic regression → ML
Multiple regression plane → ML
Nonlinear curve fitting → still ML

What makes Model 4 “feel” extra ML-ish is:

* It cannot be solved with simple algebra
* It requires **iterative numerical optimization**
* It has **convergence behavior**
* It learns from historical data
* It updates over time = adaptive model

> Models 0–3 can be solved using algebra and linear regression tools.
> Model 4 crosses the line into real machine-learning style regression because:
>
> * it’s nonlinear
> * parameters must be learned with an optimizer
> * we iteratively minimize error instead of plugging into a formula


* Model 0
  → signal processing / EMA / adaptive filter

* Model 1
  → polynomial regression

* Model 2
  → weather-feature-augmented regression

* Model 3
  → multivariate regression / linear models in feature space

* **Model 4**
  → **nonlinear regression + numerical optimization**
  → same mathematical concepts used in:

  * logistic regression training
  * neural network weight training
  * physics-informed ML models
  * curve fitting in engineering

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


## Bonus Week — Matrix Algebra for Model 3 (from scratch)

### Day B1 — Vectors & dot products (the “atoms”)

**Goal:** Get comfortable with vectors as lists and the dot product, because matrix multiply is *just dot products everywhere*.

**Mini build (10 min):**

* Implement:

  * `dot(a, b)`
  * `add(a, b)`
  * `scale(a, k)`

**Micro-exercises (10 min):**

1. Compute dot([1,2,3],[4,5,6])
2. Interpret dot as “weighted sum” (why it shows up in prediction)

**Porting note:** Every language has loops—this is 100% portable.

---

### Day B2 — Matrices as list-of-lists + transpose

**Goal:** Represent a matrix, and write `transpose(M)`.

**Mini build:**

* `transpose(X)` because **XᵀX** and **Xᵀy** are the whole regression pipeline 

**Micro-exercises:**

1. Transpose a 3×2 into a 2×3
2. Check you didn’t swap incorrectly (print rows)

---

### Day B3 — Matrix multiply (general) + “specials” you actually need

**Goal:** Implement:

* `matmul(A, B)` (general)
* `matvec(A, v)` (matrix × vector)

Then show you can compute:

* `XT = transpose(X)`
* `XTX = matmul(XT, X)`
* `XTy = matvec(XT, y)` (or treat y as Nx1 matrix)

This directly matches your manual pipeline where you compute **XᵀX** and **XᵀY** .

**Micro-exercises:**

1. Multiply a 2×3 by a 3×1
2. Confirm dimensions checks (catch bugs early)

---

### Day B4 — Solve linear systems with Gaussian elimination (recommended)

**Goal:** Solve **Aβ = b** without determinants.

Why: your current script uses **Cramer’s Rule** (fine for learning) , but **Gaussian elimination** is what you’ll want in “real” code and other languages.

**Mini build:**

* `solve(A, b)` for 3×3 using forward elimination + back substitution

**Micro-exercises:**

1. Solve a simple 3×3 where the solution is obvious
2. Add a tiny “pivot if needed” swap (even one swap is huge)

---

### Day B5 — Determinants + Cramer’s Rule (as a learning mirror)

**Goal:** Understand what your current script is doing:

* det(3×3) via Sarrus 
* Replace columns with Xᵀy and divide by det(XᵀX)

**Mini build:**

* Implement `det3(M)`
* Implement Cramer for 3×3
* Compare Cramer vs Gaussian output

**Micro-exercises:**

1. Create a case where det ≈ 0 and see failure mode (“singular matrix”)

---

### Day B6 — Conditioning, scaling, and “why regression can explode”

**Goal:** Learn the practical stuff that matters in the field:

* If features are huge or correlated, **XᵀX gets ill-conditioned**
* Your solve becomes unstable (big swings in coefficients)

**Mini build:**

* Add feature scaling:

  * scale ΔT into a reasonable range (or just divide by max ΔT)
* Optional: add tiny ridge term: **XᵀX + λI** (λ = 0.01)

**Micro-exercises:**

1. Try λ = 0 vs λ small and see coefficient stability
2. Explain in one sentence what λ does (“prevents wild coefficients”)

---

### Day B7 — Build Model 3 end-to-end (portable “reference implementation”)

**Goal:** Put it all together into a tiny module you can port to Rust/C/JS.

**End result:**

* Build X from history as `[1, dT, dT*WF]` 
* Compute XTX and XTy
* Solve for β = [α3,d, α3,a, α3,b]
* Predict: `t = β0 + β1*dT + β2*(dT*WF)` 

**Micro-exercises:**

1. Print coefficients and do one prediction (your “new day” test)
2. Compare to the scikit version for sanity 

---

## Pure-Python “portable core” you can teach and port

This is the core I’d base the week on (no NumPy, no libs). Keep it small so it fits the 20-minute format.

```python
# ----------------------------
# Vectors / matrices utilities
# ----------------------------

def transpose(M):
    rows = len(M)
    cols = len(M[0])
    return [[M[r][c] for r in range(rows)] for c in range(cols)]

def matmul(A, B):
    a_rows, a_cols = len(A), len(A[0])
    b_rows, b_cols = len(B), len(B[0])
    if a_cols != b_rows:
        raise ValueError("Dimension mismatch in matmul")
    out = [[0.0] * b_cols for _ in range(a_rows)]
    for i in range(a_rows):
        for j in range(b_cols):
            s = 0.0
            for k in range(a_cols):
                s += A[i][k] * B[k][j]
            out[i][j] = s
    return out

def matvec(A, v):
    rows, cols = len(A), len(A[0])
    if cols != len(v):
        raise ValueError("Dimension mismatch in matvec")
    out = [0.0] * rows
    for i in range(rows):
        s = 0.0
        for j in range(cols):
            s += A[i][j] * v[j]
        out[i] = s
    return out

# ----------------------------
# Solve 3x3 via Gaussian elimination (with simple pivoting)
# ----------------------------

def solve_3x3(A, b, eps=1e-12):
    # Make copies (don’t mutate caller data)
    M = [row[:] for row in A]
    y = b[:]

    n = 3

    # Forward elimination
    for col in range(n):
        # Pivot: find best row
        pivot = col
        best = abs(M[col][col])
        for r in range(col + 1, n):
            if abs(M[r][col]) > best:
                best = abs(M[r][col])
                pivot = r

        if best < eps:
            raise ValueError("Singular / ill-conditioned matrix")

        # Swap rows if needed
        if pivot != col:
            M[col], M[pivot] = M[pivot], M[col]
            y[col], y[pivot] = y[pivot], y[col]

        # Eliminate below
        for r in range(col + 1, n):
            factor = M[r][col] / M[col][col]
            # Row_r = Row_r - factor * Row_col
            for c in range(col, n):
                M[r][c] -= factor * M[col][c]
            y[r] -= factor * y[col]

    # Back substitution
    x = [0.0] * n
    for r in range(n - 1, -1, -1):
        s = y[r]
        for c in range(r + 1, n):
            s -= M[r][c] * x[c]
        x[r] = s / M[r][r]
    return x

# ----------------------------
# Model 3 fit/predict
# ----------------------------

def fit_model3(history):
    # X = [1, dT, dT*WF], y = minutes
    X = []
    y = []
    for row in history:
        X.append([1.0, float(row["dT"]), float(row["dT"]) * float(row["wf"])])
        y.append(float(row["mins"]))

    XT = transpose(X)
    XTX = matmul(XT, X)     # 3x3
    XTy = matvec(XT, y)     # 3

    beta = solve_3x3(XTX, XTy)
    return beta  # [alpha_3_d, alpha_3_a, alpha_3_b]

def predict_model3(beta, dT, wf):
    return beta[0] + beta[1]*dT + beta[2]*(dT*wf)

# Demo dataset (matches your tutorial files)
history = [
    {"dT": 3.0, "wf": 0.4, "mins": 20.0},
    {"dT": 5.0, "wf": 0.6, "mins": 35.0},
    {"dT": 7.0, "wf": 0.8, "mins": 50.0},
    {"dT": 2.0, "wf": 0.3, "mins": 15.0},
    {"dT": 6.0, "wf": 0.7, "mins": 40.0},
]

beta = fit_model3(history)
print("beta =", [round(v, 4) for v in beta])

print("prediction =", round(predict_model3(beta, dT=4.0, wf=0.5), 2), "minutes")
```

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