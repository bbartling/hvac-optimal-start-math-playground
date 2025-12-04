# hvac-optimal-start-math-playground
This repo teaches HVAC optimal-start math + contains Python learning playground material.

This reference outlines the consistent inputs and outputs used across `OptimalStartModel1` and `OptimalStartModel3` based on the PNNL paper in the $$pdf$$(https://github.com/bbartling/niagara4-vibe-code-addict/tree/develop/pdf) directory.

Also see active Java versions on the vibe coder $$repository$$(https://github.com/bbartling/niagara4-vibe-code-addict/blob/develop/README_OPT_START.md) which is actively being tested by Ben in the field in the Niagara4 framework in a `ProgramObject`.


---


<details>
<summary>📝 Model Equations Summary</summary>

The models are formulated from a simplified thermal-resistance and capacitance model (2R1C or 1R1C) of the zone dynamics.

* TODO add model zero for the Linear Model
| Model | Underlying Equation | Description |
| :--- | :--- | :--- |
| **Model 1** | $t_{opt} = \alpha_{1,a}(T_{sp} - T_{z,0})^{2} + \alpha_{1,b}$ | **Quadratic:** Assumes thermal mass is concentrated in the indoor air (1R1C model) and neglects outdoor temperature influence. Best for interior/well-insulated zones. |
| **Model 3** | $t_{opt} = \alpha_{3,a}(T_{sp} - T_{z,0}) + \alpha_{3,b}(T_{sp} - T_{z,0})\frac{(T_{sp} - T_{o})}{\alpha_{3,c}} + \alpha_{3,d}$ | **Weather Compensated:** Uses a 2R1C approximation and includes outdoor air temperature ($T_o$) influence via the second term.|


The difference in implementation stems directly from the mathematical **complexity** of the underlying models:

* TODO add model zero for the Linear Model
* **Model 1** uses a **Simple Linear Regression** formulation ($y = mx + c$), which is easy to implement manually with a basic set of equations.
* **Model 3** requires **Multiple Linear Regression** ($y = a \cdot x_1 + b \cdot x_2 + d$), which is complex and better handled by a dedicated library like scikit-learn.

---

## 4. Model Details

**Model 1: Manual Simple Regression:**
$$t = \alpha_{1,a} \cdot (\Delta T^2) + \alpha_{1,b}$$

In this formula, the duration ($t$) is the dependent variable ($y$), and the squared temperature difference ($\Delta T^2$) is the single independent variable ($x$).

* **Implementation:** Model 1 implements the core tuning logic in `_compute_regression_for_mode` by manually calculating the sums needed for the **ordinary least squares (OLS)** solution.
* **Why Manual?** Simple Linear Regression has basic, closed-form equations (the familiar $\frac{n \Sigma xy - \Sigma x \Sigma y}{n \Sigma x^2 - (\Sigma x)^2}$ formula) that are short and reliable enough to code directly without needing external libraries.


---


**Model 3: Scikit-learn for Multiple Regression**
$$t = \alpha_{3,a} \cdot \Delta T + \alpha_{3,b} \cdot \Delta T \cdot \text{WF} + \alpha_{3,d}$$

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

Each day is 10–20 minutes.
At the end, you’ll understand PNNL Model 0/1/3 completely from the math side.

---

# **WEEK 1 — Foundations of Change, Slopes, and Estimation (Algebra Refresh)**

### **Day 1 — Δ (delta), rate-of-change, degrees-per-minute**

* Computing ΔT
* Converting ΔT/min into a per-minute slope
* Why linear relationships are assumed in HVAC warm-up

**Mini-task:** compute degree-per-minute manually from 5 sample warm-up logs.

---

### **Day 2 — Linear formula refresher: y = m x + b**

* m = slope
* b = intercept
* What the slope physically means in HVAC
* Translate y = mx + b to warm-up: minutes = a*(ΔT) + b

**Mini-task:** Solve a slope/intercept from two warm-up datapoints.

---

### **Day 3 — Quadratics refresher: y = a x² + b**

* Why PNNL Model 1 uses ΔT²
* Intuition: big temperature deltas warm up disproportionately slower

**Mini-task:** given 3 datapoints, compute a & b by hand like your tutorial.

---

### **Day 4 — Systems of equations refresher**

* Solving two unknowns
* Solving three unknowns
* Use the PNNL Model 3 structure

**Mini-task:** solve a 2×2 linear system with substitution.

---

### **Day 5 — Regression without statistics**

* Linear regression as just solving equations
* Why none of this is machine learning
* How least-squares = solving the “best fit” line

**Mini-task:** calculate “best fit” slope for 3 simple points.

---

### **Day 6 — Units, consistency, dimensional analysis**

* Why warm-up models behave badly when units are mixed
* Why WF uses (Tset – OAT)/α

**Mini-task:** compute WF for 70°F, 80°F, 95°F.

---

### **Day 7 — Review & interpret sample warm-up data**

* Identify patterns
* When linear vs quadratic vs weather-based model makes sense
* Recognize bad datapoints (sensor drift, mis-setpoints, holidays)

---

# **WEEK 2 — Exponential Moving Average (EMA) Mastery**

### **Day 8 — What an EMA actually is (the simplest definition)**

$$
EMA_{new} = EMA_{old} + \alpha (x - EMA_{old})
$$

Why this is perfect for self-tuning BAS models.

---

### **Day 9 — Compute an EMA by hand**

* Use α = 0.1, 0.3, 0.7
* Show how smoothing changes with alpha

**Mini-task:** compute EMA over 5 numbers on paper.

---

### **Day 10 — How Niagara’s Optimal Start uses EMA**

* rateDegPerMin = EMA of observed rate
* observedRate = ΔT / minutes
* How this stabilizes runtime predictions

**Mini-task:** walk through one full warm-up calculation.

---

### **Day 11 — EMA vs raw average**

* Why EMA is better for building warm-up
* How EMA eliminates “jumpy” behavior
* Why it self-tunes with each new morning

---

### **Day 12 — EMA as a control loop gain**

* α = the “learning rate”
* α too small → slow learning
* α too large → unstable/erratic predictions

**Mini-task:** sketch stable vs unstable EMA behavior.

---

### **Day 13 — Double EMA (EMA of EMA)**

* How multi-day smoothing emerges naturally
* Not required in PNNL, but good to know

---

### **Day 14 — Week 2 review**

* Re-do EMA examples
* Re-express them verbally in building control terms

---

# **WEEK 3 — Self-Tuning Algebraic Optimal Start Models**

### **Day 15 — PNNL Model 0 (pure linear EMA model)**

$$
t = \frac{\Delta T}{rate_{EMA}}
$$

How this is literally the simplest self-tuning model in BAS.

---

### **Day 16 — PNNL Model 1 (quadratic algebraic tuning)**

$$
t = a(\Delta T)^2 + b
$$

* How solving two parameters = automatic tuning
* Why fitting curve to real data is self-calibration

---

### **Day 17 — Solve Model 1 by hand**

* 3 datapoints
* Solve x = ΔT²
* Solve the system
* Update a, b

---

### **Day 18 — PNNL Model 3 structure**

$$
t = a (\Delta T) + b (\Delta T \cdot WF) + d
$$

* 3 unknowns
* 3 equations → solvable
* Why WF improves accuracy

---

### **Day 19 — Solve Model 3 coefficients by hand**

Using 3 datapoints and weather factor WF.

---

### **Day 20 — How Niagara stores the coefficients**

* a = “coefficient 1”
* b = “coefficient 2”
* d = “offset”
* rateEMA (Model 0 only)
* Learning happens 1× each morning

---

### **Day 21 — Compare: linear vs quadratic vs weather models**

* When each model is best
* How to visually detect which model fits your site
* Sensor failures & data gaps

---

# **WEEK 4 — Real-World BAS Application + Coding Fluency**

### **Day 22 — Building an optimal start dataset**

* What data is needed
* How to clean warm-up data
* Ignore holidays, maintenance days, deadbands

---

### **Day 23 — Implement Model 0, 1, 3 in basic Python**

* Only add/sub/multiply/divide
* No libraries
* Like your tutorial files

---

### **Day 24 — Reinforce solving small linear systems**

* Practice writing and solving 2×2 and 3×3 systems
* Become fast at it again

---

### **Day 25 — Implement full model evaluation logic**

Given:

* zone start temp
* setpoint
* OAT
* coefficients a/b/d
  Compute time-to-setpoint.

---

### **Day 26 — Implement self-tuning update logic**

* Append datapoint
* Recompute coefficients
* Replace old coeffs with new ones

---

### **Day 27 — Compare accuracy of the models on fake/historical data**

* Quick sensitivity analysis
* How deltaT and WF affect predicted minutes

---

### **Day 28 — Identify pathological cases**

* zoneTemp = setpoint
* 0 min actual warmup
* negative deltaT
* staging, lockout, multi-stage heat pumps
* developer traps in real BAS data

---

### **Day 29 — Build your own hybrid model**

You choose:

* linear + EMA + weather
* quadratic + EMA
* or a comfort-band adaptive model

---

### **Day 30 — Final project: Build a mini-optimal-start engine**

Combine everything from the month:

* Ingest 10 datapoints
* Compute Model 0, 1, 3
* Update them with new run
* Predict tomorrow
* Compare outputs
* Interpret behavior
* Document like a Niagara README

---

# **🎉 End result after 30 days**

You will be fully fluent again in:

### **✓ EMA and why it is used**

### **✓ Solving coefficient-based algebraic models**

### **✓ Updating coefficients from new datapoints**

### **✓ Understanding how PNNL Models 0/1/3 work internally**

### **✓ Recognizing model misbehavior in BAS data**

### **✓ Mapping equations ↔ Niagara ProgramObject slots**

### **✓ Explaining optimal start math to operators and engineers**

This will give you complete confidence in:

* building
* debugging
* tuning
* and explaining

self-tuning optimal start models.


</details>


---


<details>
<summary>Day 1 — Δ (Delta), Rate-of-Change & Degrees-Per-Minute (DPM) </summary>

**30-Day Crash Course: Self-Tuning Algebraic Models & EMA**
*Day 1 is foundational. No algebra tricks. Just intuition + 3 tiny exercises.*

---

# **1. What “Δ” Actually Means (BAS + HVAC version)**

In HVAC and BAS, **Δ (delta)** simply means:

> **“How much did something change?”**

You’ve used this your whole career — this is just the math notation for it.

Examples:

* **ΔT** = change in temperature
* **Δt** = change in time
* **ΔFlow** = change in CFM
* **ΔkW** = change in power
* **ΔSP** = change in setpoint

In warm-up / optimal start problems:

$$
\Delta T = T_{setpoint} - T_{zone,start}
$$

That’s it — delta is just subtraction.

---

# **2. Rate of Change (Slope) Refresher**

HVAC warm-up is all about **how fast** the temperature rises.

In controls we usually talk about:

* °F/min
* °F/hr
* kW/min
* psi/sec

Mathematically this is:

$$
\text{Rate} = \frac{\Delta T}{\Delta t}
$$

**Important:**
In optimal start models, the **rate of temperature change** is literally the **degree-per-minute** (DPM) number used in Niagara’s Model 0.

---

# **3. Why This Matters for Optimal Start**

If you know:

* how many degrees you are away from setpoint (**ΔT**)
* how many degrees per minute you can warm up (**rate**)

Then predicted warm-up time is:

$$
t = \frac{\Delta T}{\text{rate}}
$$

This is the **entire foundation** of Model 0 (Linear EMA model).

All advanced models (Model 1, Model 3) still rely on the idea of ΔT and warming “rate,” they just model the rate differently.

---

# **4. Mini-Examples (super quick)**

### **Example A — Compute ΔT**

Zone = **65°F**
Setpoint = **72°F**

$$
\Delta T = 72 - 65 = 7^\circ F
$$

Easy.

---

### **Example B — Compute rate-of-change (DPM)**

Start = 65°F
End = 72°F
Time = 35 minutes

$$
\Delta T = 7^\circ F
$$

$$
\text{rate} = \frac{7}{35} = 0.20^\circ F/\text{min}
$$

This **0.20°F/min** is what Niagara stores in `degreesPerMinute`.

---

### **Example C — Predict warm-up time**

Let’s reuse the rate above.

Zone = 68°F
SP = 72°F
ΔT = 4°F
Rate = 0.20°F/min

$$
t = \frac{4}{0.20} = 20\ \text{minutes}
$$

That’s it — **Model 0 prediction**.

---

# **5. Day 1 Micro-Exercise (Do This Now)**

Just 3 fast problems.

### **1️⃣ Compute ΔT**

* Zone = 67°F
* SP = 72°F ⇒ ΔT = ?

### **2️⃣ Compute Rate**

* Start = 64°F
* End = 72°F
* Time = 30 min ⇒ DPM = ?

### **3️⃣ Predict Warm-Up Time**

* ΔT = 6°F
* Rate = 0.25°F/min ⇒ minutes = ?

*You can message me answers or I can check them.*

---

# **6. Key Takeaway From Day 1**

You only need **two core ideas** to understand the entire world of Optimal Start:

### **✓ Temperature difference (ΔT)**

How much warming/cooling is needed?

### **✓ Warm-up rate (°F per minute)**

How fast can the building respond?

Everything else — EMA, regression, self-tuning — builds directly on these two concepts.

---

# Ready for **Day 2** (Slope & Intercept refresher)?


</details>



---


<details>
<summary> Day 2 — Linear Formula Refresher: y = m·x + b (HVAC Warm-Up Edition) </summary>

**30-Day Crash Course: Self-Tuning Algebraic Models & EMA**
*Today is all about restoring intuition for linear equations — the backbone of Model 0 and the starting point for Models 1 & 3.*

---

# **1. What y = m·x + b Really Means (Controls-Friendly Version)**

You’ve seen this a thousand times, but today we translate it into **HVAC physics**.

The classic line equation:

$$
y = m x + b
$$

Breaks down into:

* **y** → the output you want (predicted warm-up minutes)
* **x** → the input (ΔT, or sometimes ΔT², or ΔT·WF)
* **m** → slope (how sensitive minutes are to ΔT)
* **b** → intercept (baseline warm-up time even when ΔT = 0)

In other words:

> **m = how many minutes per degree**
> **b = your fixed overhead** (like fan start lag, coil heating inertia, sensor lag)

This is EXACTLY how PNNL and Niagara use slope/intercept inside optimal start.

---

# **2. How it applies to Optimal Start**

Let’s map it directly.

### If

$$
t = a\cdot\Delta T + b
$$

Then:

* **a** = minutes per degree (inverse of DPM)
* **b** = your “dead” time that always occurs no matter what

  * Example: the first ~5 minutes before coils meaningfully raise zone temp
  * Or preheat valve stroking delays
  * Or VAV boxes opening slowly

Niagara’s Model 0 does NOT use explicit slope/intercept, but Model 1 and Model 3 DO — they just compute them from data automatically.

---

# **3. Slopes in HVAC Warm-Up (Practical Intuition)**

Let’s say your building typically warms at:

* 0.20°F/min (Day 1 example)

The inverse is:

$$
\frac{1}{0.20} = 5\ \text{min per degree}
$$

This 5 minutes/°F is your *slope*.
In linear form:

$$
t = 5(\Delta T) + b
$$

Then the **intercept b** might be:

* 5–8 minutes of “thermal inertia” overhead
* Coil heat-up time
* Duct temperature lag
* Straggler sensors
* Communication lag from field devices

So maybe:

$$
t = 5(\Delta T) + 7
$$

That’s a **valid Model-1-like linear warm-up approximation**.

---

# **4. Solve a Linear Model by Hand (Easy Example)**

Suppose you collected two warm-up data points:

| ΔT  | Actual Minutes |
| --- | -------------- |
| 5°F | 33 min         |
| 3°F | 22 min         |

Use the two points to solve for **m** and **b**.

### Step 1 — Two equations

$$
\begin{aligned}
33 &= 5m + b \
22 &= 3m + b
\end{aligned}
$$

### Step 2 — Subtract equations

$$
(33 - 22) = (5m - 3m)
$$

$$
11 = 2m
$$

$$
m = 5.5\ \text{min/°F}
$$

### Step 3 — Plug back to find b

Use 22 = 3m + b:

$$
22 = 3(5.5) + b
$$

$$
22 = 16.5 + b
$$

$$
b = 5.5\ \text{minutes}
$$

### Final linear warm-up model:

$$
t = 5.5(\Delta T) + 5.5
$$

Notice how nicely that makes sense:

* About 5½ minutes per degree
* About 5½ minutes overhead

This is exactly what Niagara is computing in the background in Model 1 and Model 3.

---

# **5. Mini-Examples (super quick)**

### **Example A — Predict warm-up**

$$
t = 4(ΔT) + 6
$$

If ΔT = 8°F:

$$
t = 4×8 + 6 = 38\ \text{min}
$$

---

### **Example B — Find slope from two points**

(ΔT = 4°F, minutes = 32)
(ΔT = 6°F, minutes = 46)

Slope:

$$
m = \frac{46 - 32}{6 - 4} = \frac{14}{2} = 7\ \text{min/°F}
$$

---

### **Example C — Interpret intercept**

If
$$
t = 6ΔT + 10
$$

then **10 min** means:

* coil warm-up
* duct thermal lag
* sensor lag
* control delays
* motor speeds ramping up

This “fixed overhead time” is why simple t = ΔT/rate is sometimes too optimistic — Model 1 fixes this.

---

# **6. Day 2 Micro-Exercise (Do This Now)**

Just 3 quick linear tasks.

### **1️⃣ Solve slope m**

Points: (ΔT=2, t=15) and (ΔT=6, t=27)
m = ?

---

### **2️⃣ Solve intercept b**

Use your m above and the point (6, 27)

---

### **3️⃣ Predict warm-up**

Using your found equation (t = mΔT + b), solve for ΔT = 5°F.

---

Send me your answers or ask me to check them.

---

# **Key Takeaway From Day 2**

Everything — EMA, Models 1 & 3, self-tuning — ultimately plugs back into:

$$
t = m x + b
$$

It’s all slope and intercept with different definitions of “x.”

We’re just tuning the slope **and** the intercept automatically as new warm-up data comes in.

---

# **Ready for Day 3 (Quadratics refresher)?**



</details>


---


<details>
<summary>Day 3 — Quadratics Refresher: Why Model 1 Uses (ΔT)</summary>


**30-Day Crash Course: Self-Tuning Algebraic Models & EMA**
*Today brings in the idea of curvature — the foundation of PNNL Model 1’s shape.*

---

# **1. Why Quadratics Show Up in HVAC Warm-Up**

Real buildings do **not** warm up linearly as ΔT gets larger.

* If ΔT is small (2–4°F), warm-up is almost linear.
* If ΔT is big (8–12°F), the building warms *slower per degree* as ΔT increases.

This is because:

* Coil capacity is fixed.
* Heat transfer slows as zone air gets closer to discharge temperature.
* Envelope losses increase with ΔT.
* Big ΔT events usually happen on cold mornings when OAT is low.

A simple linear model:

$$
t = m\Delta T + b
$$

**underestimates** runtime for large ΔT.

A quadratic:

$$
t = a(\Delta T)^2 + b
$$

**adds curvature** — meaning:

> “The more ΔT you have, the more minutes each extra degree costs.”

This is exactly what PNNL’s **Model 1** does.

---

# **2. What a Quadratic Curve Looks Like (HVAC Interpretation)**

The curve is shaped like:

* Slow rise at small ΔT
* Faster rise at large ΔT

Graphically (simplified):

```
minutes
  ^
  |            *
  |        *
  |    *
  | *
  +------------------> ΔT
       small → large
```

This shape matches real building warm-ups much better than a straight line.

---

# **3. The Algebra Behind Model 1 (Super Simple)**

Model 1 formula:

$$
t = a(\Delta T)^2 + b
$$

Where:

* **a** controls curvature
* **b** is the baseline overhead (same idea as linear intercept)

If ΔT doubles, warm-up time more than doubles.

Example:

If:
a = 0.6
b = 6

Then:

| ΔT  | t = aΔT² + b          |
| --- | --------------------- |
| 2°F | 0.6·4 + 6 = 8.4 min   |
| 4°F | 0.6·16 + 6 = 15.6 min |
| 8°F | 0.6·64 + 6 = 44.4 min |

Notice:

* ΔT doubled from 4 → 8°F
* Warm-up did **NOT** double (15.6 → 44.4 min)
* It almost **tripled** instead
* This is exactly what we need for cold mornings

---

# **4. Solve a Quadratic Model by Hand (Easy HVAC Example)**

Suppose you collected 3 warm-up datapoints:

| ΔT  | Minutes |
| --- | ------- |
| 2°F | 10 min  |
| 4°F | 20 min  |
| 6°F | 38 min  |

Step 1 — Compute x = ΔT²

| ΔT | x (ΔT²) |
| -- | ------- |
| 2  | 4       |
| 4  | 16      |
| 6  | 36      |

Step 2 — Write equations

$$
\begin{aligned}
10 &= a(4) + b \
20 &= a(16) + b \
38 &= a(36) + b
\end{aligned}
$$

Step 3 — Use any two to solve for a and b
Let’s subtract equations 2 & 1:

$$
(20 - 10) = a(16 - 4)
$$

$$
10 = 12a
$$

$$
a = \frac{10}{12} = 0.8333
$$

Now plug into eq. 1:

$$
10 = 4(0.8333) + b
$$

$$
10 = 3.333 + b
$$

$$
b = 6.667
$$

Final quadratic warm-up model:

$$
t = 0.8333(\Delta T)^2 + 6.667
$$

This is PNNL Model 1 in action, computed entirely from real field data.

---

# **5. Mini-Examples (super quick)**

### **Example A — Predict warm-up**

$$
t = 0.5(\Delta T)^2 + 4
$$

If ΔT = 7°F:

$$
t = 0.5(49) + 4 = 28.5\ \text{min}
$$

---

### **Example B — Interpret curvature**

If a = 1.0:

* Every extra degree adds more minutes than the one before
* The building warms slower when cold → realistic

---

### **Example C — What if ΔT is small?**

If ΔT = 1–3°F:

Quadratic model almost **looks linear**:

| ΔT | ΔT² |
| -- | --- |
| 1  | 1   |
| 2  | 4   |
| 3  | 9   |

For small ranges, a straight line approximates very well.
This is why **Model 0 works fine in mild climates**.

---

# **6. Day 3 Micro-Exercise (Do This Now)**

### **1️⃣ Compute x = (ΔT)²**

For ΔT = 3, 5, 7.

---

### **2️⃣ Using the model t = 0.7x + 6, predict warm-up**

For your x values above.

---

### **3️⃣ Think practically**

Does your building warm up linearly or quadratically for large ΔT?
(There is no wrong answer — just think in terms of your real buildings.)

---

Send your answers if you want me to check them.

---

# **Key Takeaway From Day 3**

Quadratic models:

* Capture slow warm-up at large ΔT
* Fit cold-morning behavior better
* Are solved using the **same simple algebra** as Day 2
* Form the basis of **PNNL Model 1**

The math is still simple — ΔT, ΔT², slope, intercept — just arranged differently.

---

# **Ready for Day 4 (Systems of Equations refresher)?**

Just say: **“Day 4 please.”**


</details>

---


<details>
<summary>Day 4 — Systems of Equations Refresher (Foundation of Model 3)</summary>


**30-Day Crash Course: Self-Tuning Algebraic Models & EMA**
*Today we learn how to solve two and three equations — the math engine behind Model 1 & Model 3.*

---

# **1. Why Systems of Equations Matter in Optimal Start**

In **Model 1**, you solve for **two unknowns**:

$$
t = a(\Delta T)^2 + b
$$

Unknowns:

* **a** (curvature)
* **b** (intercept)

You need **two equations** (two datapoints) to solve it.

---

In **Model 3**, you solve for **three unknowns**:

$$
t = a(\Delta T) + b(\Delta T \cdot WF) + d
$$

Unknowns:

* a
* b
* d

You need **three equations** (three datapoints) to solve this.

---

### Systems of equations = “use building data to solve for model coefficients.”

This is the heart of **self-tuning**.

---

# **2. Warm-Up Example of a 2×2 System**

Given:

$$
\begin{aligned}
16 &= 9a + b \
30 &= 25a + b
\end{aligned}
$$

This came from your earlier Model 1 example.

Goal: eliminate **b**.

Subtract the first equation from the second:

$$
(30 - 16) = (25a - 9a)
$$

$$
14 = 16a
$$

$$
a = \frac{14}{16} = 0.875
$$

Then solve for **b**:

$$
16 = 9(0.875) + b
$$

$$
16 = 7.875 + b
$$

$$
b = 8.125
$$

That’s the whole method.
PNNL Model 1 internally does exactly this.

---

# **3. Warm-Up Example of a 3×3 System (Model 3 Style)**

You don’t need to solve this by hand today — just understand the structure.

Model 3 formula:

$$
t = a(\Delta T) + b(\Delta T \cdot WF) + d
$$

Each datapoint creates one equation:

### Datapoint 1:

$$
t_1 = a x_{11} + b x_{12} + d
$$

### Datapoint 2:

$$
t_2 = a x_{21} + b x_{22} + d
$$

### Datapoint 3:

$$
t_3 = a x_{31} + b x_{32} + d
$$

Where:

* (x_{i1} = \Delta T_i)
* (x_{i2} = \Delta T_i \cdot WF_i)

This creates a **3×3 system** you solve for **a, b, d**.

Niagara does this automatically.
You just need to know why it works.

---

# **4. A Very Simple 2×2 Example for You to Practice**

Solve the system:

$$
\begin{aligned}
8 &= 2m + b \
20 &= 6m + b
\end{aligned}
$$

### Step 1 — Subtract equations

$$
(20 - 8) = (6m - 2m)
$$

$$
12 = 4m
$$

$$
m = 3
$$

### Step 2 — Solve for b

Use 8 = 2m + b:

$$
8 = 2(3) + b
$$

$$
8 = 6 + b
$$

$$
b = 2
$$

### ✔ Final model:

$$
t = 3\Delta T + 2
$$

**That’s a realistic warm-up equation.**

---

# **5. Mini-Examples (super quick)**

### **Example A — Solve the system**

$$
\begin{aligned}
18 &= 3k + c \
30 &= 5k + c
\end{aligned}
$$

Find **k** and **c**.

---

### **Example B — Interpret “c” in HVAC terms**

If:

$$
t = 4\Delta T + 7
$$

Then **7 minutes** is your:

* warm-up overhead
* sensor lag
* coil lag
* duct temperature delay

---

### **Example C — Why Model 3 needs 3 equations**

Because:

* 3 unknowns → a, b, d
* Need 3 datapoints → 3 warm-up mornings
* System must be solvable → not colinear or degenerate

---

# **6. Day 4 Micro-Exercise (You Solve These)**

Solve this 2×2 system:

$$
\begin{aligned}
14 &= 4a + b \
26 &= 8a + b
\end{aligned}
$$

### What to do:

1. Subtract equations → solve for **a**
2. Plug a back in → solve for **b**
3. Tell me your final model:

$$
t = a(\Delta T) + b
$$

Send me:

* **a = ?**
* **b = ?**

…and I’ll verify it.

---

# **Key Takeaway from Day 4**

Systems of equations are **the engine** behind:

* Model 1 (2×2 system)
* Model 3 (3×3 system)
* Any future hybrid self-tuning model you build

They allow the BAS to **solve for coefficients** directly from real warm-up data — making the model “learn.”



</details>

---


<details>
<summary>Day 5 </summary>

Here is **📘 Day 5**, written in the exact same structured, HVAC-friendly, intuitive style as Days 1–4.

---

# **📘 Day 5 — Regression Without Statistics (Just Algebra)**

**30-Day Crash Course: Self-Tuning Algebraic Models & EMA**
*Today we learn how “regression” in optimal start is nothing more than solving simple equations — no statistics package, no sci-py, no calculus.*

---

# **1. Why regression ≠ statistics in optimal start**

When people hear *regression*, they imagine:

* big data
* least-squares solvers
* linear algebra libraries
* machine learning

But in the context of HVAC optimal start, regression is simply:

> “Solve for the coefficients that best fit your warm-up data.”

That’s it.

### For Model 1:

$$
t = a x + b
$$
(where (x = \Delta T^2))

### For Model 3:

$$
t = a x_1 + b x_2 + d
$$
(where (x_1 = \Delta T) and (x_2 = \Delta T \cdot WF))

You’re just solving 2 or 3 equations with 2 or 3 unknowns.

Pure algebra.
No statistics.
No randomness.
No probability.

---

# **2. Why solving a line through two points *is* regression**

If you have two warm-up datapoints:

$$
(x_1, t_1)
$$

$$
(x_2, t_2)
$$

You do:

$$
m = \frac{t_2 - t_1}{x_2 - x_1}
$$

$$
b = t_1 - m x_1
$$

This is literally a regression.
It is the best possible line through those two points.

The only difference is:

* **Model 0** → no regression, just EMA
* **Model 1** → 2-point algebraic regression
* **Model 3** → 3-point algebraic regression

Everything is solvable by hand.

---

# **3. Why this is good news for BAS controls**

* You never need numpy or sklearn
* Niagara runs this in real-time
* BAS techs can understand tuning behavior
* It’s explainable
* It’s transparent
* It matches the physics (ΔT drives minutes)

This is why PNNL chose these models — they’re powerful but simple enough to run in a controller.

---

# **4. A Clean Example of Algebraic Regression**

You have two warmed-up datapoints:

| ΔT | x = ΔT² | t  |
| -- | ------- | -- |
| 3  | 9       | 14 |
| 7  | 49      | 50 |

Solve:
$$
t = a x + b
$$

### Step 1 — Compute slope (a)

$$
a = \frac{50 - 14}{49 - 9}
$$

$$
a = \frac{36}{40} = 0.9
$$

### Step 2 — Solve for intercept (b)

$$
14 = 9(0.9) + b
$$

$$
14 = 8.1 + b
$$

$$
b = 5.9
$$

### Final regression model:

$$
t = 0.9x + 5.9
$$

You just performed a regression.

---

# **5. Regression intuition for HVAC engineers**

If the building warms *faster*:

* slope becomes smaller
* intercept may shrink

If the building warms *slower*:

* slope becomes larger
* intercept grows

The math tells the story of the building.

When your operators say:

> “The building took longer this morning.”

Your model will automatically adjust the slope upward.

This is the heart of **self-tuning** behavior.

---

# **6. Mini-Examples (super quick)**

### **Example A — Solve the regression**

Points:
(ΔT² = 4, t = 10)
(ΔT² = 25, t = 40)

Find **a** and **b**.

---

### **Example B — Rerun slope if new data arrives**

Old points:
(9, 20) → 20 min
(25, 40) → 40 min

New morning datapoint:
(16, 30) → 30 min

How will the slope **change**?

### Hint:

* old slope was (40 – 20)/(25 – 9)
* new slope should reflect faster warm-up

---

### **Example C — Interpret b**

If:

$$
t = 0.6x + 8
$$

Then:

* **8 minutes** = fixed overhead (lag, valve stroking, coil heating, duct warm-up)
* **0.6x** = ΔT²-driven part of runtimes

---

# **7. Day 5 Micro-Exercise (You Solve This)**

You have these warm-up datapoints:

| ΔT | x = ΔT² | t  |
| -- | ------- | -- |
| 4  | 16      | 26 |
| 6  | 36      | 44 |

Solve:

$$
t = a x + b
$$

### What to do:

1. Compute
   $$
   a = \frac{44 - 26}{36 - 16}
   $$

2. Solve for
   $$
   b = t_1 - ax_1
   $$

3. Give me your final equation:

$$
t = a x + b
$$

I’ll check your result.

---

# **Key Takeaway From Day 5**

Regression in HVAC optimal start is nothing more than:

* Compute ΔT
* Square it (Model 1)
* Solve a simple line through two points
* Store the coefficients
* Update tomorrow

It’s algebra — not statistics, not machine learning.


</details>

---


<details>
<summary>Day 6 </summary>
Here is **📘 Day 6**, following the exact same tone, format, and “BAS-tech friendly algebra” style as Days 1–5.
Today is a BIG ONE — this is where **self-tuning** actually becomes intuitive.

---

# **📘 Day 6 — What “Self-Tuning” Really Means (No Statistics, No ML)**

**30-Day Crash Course: Self-Tuning Algebraic Models & EMA**
*Today you learn how Niagara Models 0, 1, and 3 “update themselves” each morning.*

---

# **1. Why HVAC Models Must Self-Tune**

Buildings **change constantly**:

* weather
* occupancy
* equipment degradation
* morning sun
* economizer position
* someone left the door open
* coil fouling
* VAV minimums changed
* night setback changed

A fixed model would be wrong within **weeks**.

Thus:

> **Every morning is a new data point.
> Every morning the model retunes itself.**

This is why optimal start works in real buildings.

---

# **2. Two Flavors of Self-Tuning**

There are really only two types:

---

## **Type 1 — Self-tuning with EMA (Model 0)**

This handles **single-slope** models.

Niagara’s linear model uses:

$$
\text{newRate} = \alpha \cdot \text{measuredRate} + (1 - \alpha)\cdot \text{oldRate}
$$

Where:

* **measuredRate** = “today's actual °F/min”
* **oldRate** = yesterday’s remembered rate
* **α** (“alpha”) = weight factor (0.05–0.20 typically)

You can do this with NO stats library.

Just algebra and a loop.

---

## **Type 2 — Self-tuning via Algebraic Regression (Model 1, Model 3)**

This handles models with **coefficients**:

* Model 1: `a`, `b`
* Model 3: `a`, `b`, `d`

Every morning:

* one new point → update coefficients
* old coefficients get blended with new (very light smoothing)

Think:

> **Today’s observed warm-up redefines the line (or plane).**

It’s not machine learning.
It’s not a statistical package.
It’s literally:
**Solve two equations for a and b again.**

---

# **3. Self-Tuning Example — Linear EMA (Model 0)**

Let’s say:

* Yesterday’s DPM = **0.20°F/min**
* Today you actually warmed:

$$
\Delta T = 6^\circ
$$

$$
\Delta t = 30\ \text{min}
$$

So actual = (6 / 30 = 0.20°F/min) ← same as before.

If α = 0.10:

$$
\text{newRate} = 0.10(0.20) + 0.90(0.20)
$$

Same result — building is consistent.

Now imagine today had a poor warm-up:

$$
\Delta T = 6^\circ
$$

$$
\Delta t = 40\ \text{min}
$$

MeasuredRate = 6/40 = **0.15**

Now:

$$
\text{newRate} = 0.10(0.15) + 0.90(0.20)
$$

$$
= 0.015 + 0.18 = 0.195°F/min
$$

New slope nudges downward — building is slower.

This is **self-tuning in one line of Python**.

---

# **4. Self-Tuning Example — Model 1 Regression**

Two new warm-up datapoints:

| ΔT | x = ΔT² | t  |
| -- | ------- | -- |
| 5  | 25      | 38 |
| 9  | 81      | 82 |

Solve:

$$
t = a x + b
$$

You solve:

$$
a = \frac{82 - 38}{81 - 25}
$$

$$
b = 38 - 25a
$$

This gives today’s new coefficients.

To self-tune:

$$
a_{\text{new}} = 0.85 a_{\text{old}} + 0.15 a_{\text{today}}
$$

$$
b_{\text{new}} = 0.85 b_{\text{old}} + 0.15 b_{\text{today}}
$$

That’s it.

No machine learning.
Just weighted updating.

This is *exactly* how Niagara does it.

---

# **5. Why Smoothing Is Required**

Buildings are noisy.

If you fully replaced coefficients every morning:

* one strange morning ruins the model
* VAV faults distort the slope
* cold start after a holiday shifts predictions wildly
* false starts from bad SP changes corrupt warm-up data

Smoothing makes the model **stable**.

The blend factor:

* typically 0.05–0.25
* same concept as EMA
* just applied to coefficients instead of rates

---

# **6. Mini-Examples (you try)**

### **Example A — EMA update**

OldRate = 0.18
MeasuredRate = 0.24
α = 0.15

Compute:

$$
\text{newRate} = \alpha M + (1 - \alpha)O
$$

---

### **Example B — Algebraic update**

Old a = 1.1
Old b = 8.0

Today you solve:

$$
a_{today} = 1.5,\quad b_{today} = 6.0
$$

Blend with α = 0.10:

Compute:

$$
a_{\text{new}}
$$

$$
b_{\text{new}}
$$

---

# **7. Day 6 Micro-Exercise (Your turn)**

You observed a warm-up:

* ΔT = 8°F
* Warm-up time = 55 min

Old model:

$$
t = 0.9x + 10
$$

Where:

$$
x = (\Delta T)^2
$$

### Step 1 — Compute today’s measured predicted_time

Today’s prediction:

$$
x = 8^2 = 64
$$

$$
t_{predicted} = 0.9(64) + 10
$$

### Step 2 — Compare predicted vs actual

Actual = 55 min

Was the model too fast or too slow?

### Step 3 — Update using α = 0.10

Blend the coefficients:

$$
a_{\text{new}} = 0.9(1 - \alpha) + a_{today}\alpha
$$

But you must compute **a_today** using:

$$
a_{today} = \frac{t_{actual2} - t_{actual1}}{x_2 - x_1}
$$

Hint: You only have ONE point, so assume b stays constant for today.

*(This is how Niagara handles 1-point updates.)*

---

# ⭐ Key Takeaway From Day 6

Self-tuning is nothing fancy:

* **Model 0** → EMA of warming rate
* **Model 1** → regression coefficients updated with smoothing
* **Model 3** → multivariable regression updated with smoothing

It’s all algebra + weighted averages.

That’s it.

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