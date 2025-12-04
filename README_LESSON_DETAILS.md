# HVAC Optimal Start — 30-Day Lesson Details

This document contains the **full 30-day crash course** on self‑tuning algebraic models and EMA for HVAC optimal start.  
It is meant to sit next to the main `README.md` and go deep on the math in a **BAS‑tech friendly** way — no statistics libraries, no heavy calculus, just HVAC‑flavored algebra, examples, and tiny exercises.

---

## Day 1 — Δ (Delta), Rate‑of‑Change & Degrees‑Per‑Minute (DPM)

**Goal:** Get comfortable with basic “change” notation and rate‑of‑change in HVAC warm‑up problems.

### 1. What “Δ” Actually Means (BAS + HVAC Version)

In HVAC and BAS, **Δ (delta)** just means:

> “How much did something change?”

Common examples:

- **ΔT** = change in temperature  
- **Δt** = change in time  
- **ΔFlow** = change in CFM  
- **ΔkW** = change in power

In warm‑up / optimal start problems:

$$
\Delta T = T_{setpoint} - T_{zone,start}
$$

That’s just “how many degrees we need to gain” before we hit setpoint.

### 2. Rate of Change (Slope) Refresher

Warm‑up is all about **how fast** the zone is moving toward setpoint.

Mathematically:

$$
\text{Rate} = \frac{\Delta T}{\Delta t}
$$

Typical units:

- °F/min  
- °F/hr  
- kW/min  

In Model 0, the **rate of temperature change** in °F/min is what Niagara stores as its “degrees per minute” learning value.

### 3. Why This Matters for Optimal Start

If you know:

- how many degrees you are away from setpoint (**ΔT**), and  
- how many degrees per minute you can warm up (**rate**),

then the predicted warm‑up time is:

$$
t = \frac{\Delta T}{\text{rate}}
$$

This is the core of the **linear EMA model (Model 0)**.

### 4. Mini‑Examples

**Example A — Compute ΔT**

Zone = 65°F, Setpoint = 72°F:

$$
\Delta T = 72 - 65 = 7^\circ F
$$

**Example B — Compute rate‑of‑change**

Start = 65°F, End = 72°F, Time = 35 minutes:

$$
\Delta T = 7^\circ F
$$

$$
\text{rate} = \frac{7}{35} = 0.20^\circ F/\text{min}
$$

**Example C — Predict warm‑up time**

Zone = 68°F, Setpoint = 72°F, rate = 0.20°F/min:

$$
\Delta T = 4^\circ F
$$

$$
t = \frac{4}{0.20} = 20\ \text{minutes}
$$

### 5. Day 1 Micro‑Exercise

1. Zone = 67°F, SP = 72°F → compute ΔT.  
2. Start = 64°F, End = 72°F, Time = 30 min → compute rate in °F/min.  
3. ΔT = 6°F, rate = 0.25°F/min → compute minutes to setpoint.

### 6. Key Takeaway

You only need two ideas for optimal start:

- **Temperature difference (ΔT)**: how far you are from setpoint.  
- **Warm‑up rate (°F/min)**: how fast the building can move.

Everything else (EMA, regression, self‑tuning) builds directly on these.

---

## Day 2 — Linear Formula Refresher: \(y = m x + b\) (HVAC Warm-Up Edition)

**Goal:** See how the classic line equation maps to “minutes vs ΔT” in a building.

### 1. What \(y = m x + b\) Really Means


The standard line:

$$
y = m x + b
$$

translates to:

- **y** → output (predicted minutes of warm‑up)  
- **x** → input (often ΔT)  
- **m** → slope (minutes per degree)  
- **b** → intercept (baseline minutes even when ΔT = 0)

### 2. Warm‑Up Interpretation

We write:

$$
t = a \cdot \Delta T + b
$$

Where:

- **a** ≈ minutes per degree (inverse of °F/min)  
- **b** ≈ fixed overhead: valve stroking, coil warm‑up, duct heat‑up, sensor lag, etc.

So if:

- ΔT = 0 but  
- b = 10,

you’d still expect about 10 minutes of “overhead” on a typical morning.

### 3. Solve a Linear Model by Hand

Suppose you observe:

- ΔT = 5°F → Time = 33 min  
- ΔT = 3°F → Time = 22 min  

Set up equations:

$$
\begin{aligned}
33 &= 5m + b \\
22 &= 3m + b
\end{aligned}
$$

Subtract the second from the first:

$$
33 - 22 = (5m - 3m)
$$

$$
11 = 2m \Rightarrow m = 5.5
$$

Plug back into one equation:

$$
22 = 3(5.5) + b
$$

$$
22 = 16.5 + b \Rightarrow b = 5.5
$$

Final linear warm‑up model:

$$
t = 5.5(\Delta T) + 5.5
$$

### 4. Micro‑Exercise

You saw:

- ΔT = 4°F → 26 min  
- ΔT = 6°F → 38 min  

1. Form the two equations.  
2. Solve for slope **m** and intercept **b**.  
3. Write the final form `t = m \Delta T + b`.

---

## Day 3 — Quadratics Refresher: Why Model 1 Uses `(\Delta T)^2`

**Goal:** Understand why PNNL Model 1 uses a squared term and how to work with it.

### 1. Why Quadratics Show Up in Warm‑Up

If you try a simple linear model:

$$
t = m \Delta T + b
$$

it often **underestimates** runtime for large ΔT. In many buildings:

- Small ΔT → warm‑up is efficient.  
- Large ΔT → each extra degree takes *more* time.

A quadratic:

$$
t = a (\Delta T)^2 + b
$$

captures this “curving upward” behavior. That’s what PNNL **Model 1** does.

### 2. Introduce `x = (\Delta T)^2`

To simplify, we define:

$$
x = (\Delta T)^2
$$

Then:

$$
t = a x + b
$$

Now it’s just a **line** in terms of x and t.

### 3. Micro Example of Using a Quadratic Model

Suppose the model is:

$$
t = 0.7x + 6
$$

and we want to predict for:

- ΔT = 3°F → `x = 9`  
- ΔT = 5°F → `x = 25`  
- ΔT = 7°F → `x = 49`

Compute:

- For x = 9: `t = 0.7 \cdot 9 + 6 = 12.3`  
- For x = 25: `t = 0.7 \cdot 25 + 6 = 23.5`  
- For x = 49: `t = 0.7 \cdot 49 + 6 = 40.3`

Notice time grows faster than ΔT — that’s the “curvature”.

### 4. Solve a Quadratic Model by Hand

Suppose you have:

- ΔT = 2°F → t = 10 min  
- ΔT = 4°F → t = 20 min  

Compute x:

- ΔT = 2 → x = 4  
- ΔT = 4 → x = 16  

Equations:

$$
\begin{aligned}
10 &= 4a + b \\
20 &= 16a + b
\end{aligned}
$$

Subtract:

$$
10 = 12a \Rightarrow a \approx 0.8333
$$

Then:

$$
10 = 4(0.8333) + b \Rightarrow b \approx 6.667
$$

So:

$$
t \approx 0.8333 (\Delta T)^2 + 6.667
$$

### 5. Micro‑Exercise

You observe:

- ΔT = 3°F → t = 16 min  
- ΔT = 7°F → t = 52 min  

1. Compute x = (ΔT)² for both points.  
2. Solve for a and b in `t = a x + b`.  
3. Optionally, predict t for ΔT = 5°F.

---

## Day 4 — Systems of Equations (Foundation of Model 3)

**Goal:** Get comfortable solving for 2 or 3 unknowns from multiple equations.

### 1. Why Systems Matter in Optimal Start

- **Model 1** has two unknowns: `t = a (\Delta T)^2 + b`.  
- **Model 3** has three unknowns:

  $$
  t = a(\Delta T) + b(\Delta T \cdot WF) + d
  $$

To solve for:

- Model 1: need **2 equations** (2 datapoints).  
- Model 3: need **3 equations** (3 datapoints).

### 2. Example: 2×2 System (Model 1 Style)

Given:

$$
\begin{aligned}
16 &= 9a + b \\
30 &= 25a + b
\end{aligned}
$$

Subtract:

$$
14 = 16a \Rightarrow a = 0.875
$$

Then:

$$
16 = 9(0.875) + b \Rightarrow b = 8.125
$$

### 3. Example: 3×3 System (Model 3 Structure)

Model 3:

$$
t = a(\Delta T) + b(\Delta T \cdot WF) + d
$$

Each datapoint gives:

$$
t_i = a x_{i1} + b x_{i2} + d
$$

where:

- `x_{i1} = \Delta T_i`  
- `x_{i2} = \Delta T_i \cdot WF_i`

You get three equations, three unknowns — solvable by algebra or a small matrix solve.

### 4. Micro‑Exercise

Solve:

$$
\begin{aligned}
14 &= 4a + b \\
26 &= 8a + b
\end{aligned}
$$

1. Subtract to get a.  
2. Plug back to get b.  
3. Write `t = a \Delta T + b`.

---

## Day 5 — Regression Without Statistics (Just Algebra)

**Goal:** See that “regression” here is simply “solve a line through data points”.

### 1. Regression in This Context

For optimal start:

- **Model 1**:

  $$
  t = a x + b, \quad x = (\Delta T)^2
  $$

- **Model 3**:

  $$
  t = a x_1 + b x_2 + d, \quad x_1 = \Delta T,\ x_2 = \Delta T \cdot WF
  $$

“Regression” just means: choose a, b (and maybe d) to fit datapoints well.

### 2. Two‑Point Linear Regression

Given two points `(x_1, t_1)` and `(x_2, t_2)`:

Slope:

$$
a = \frac{t_2 - t_1}{x_2 - x_1}
$$

Intercept:

$$
b = t_1 - a x_1
$$

This is the best line through those two points.

### 3. Example

You have:

- x = 9, t = 14  
- x = 49, t = 50  

Compute:

$$
a = \frac{50 - 14}{49 - 9} = \frac{36}{40} = 0.9
$$

Then:

$$
14 = 9(0.9) + b \Rightarrow b = 5.9
$$

So:

$$
t = 0.9 x + 5.9
$$

### 4. Micro‑Exercise

You observed:

- ΔT = 4°F → t = 26 min → x = 16  
- ΔT = 6°F → t = 44 min → x = 36  

1. Compute a using the two x,t pairs.  
2. Compute b using `b = t_1 - a x_1`.  
3. Write final `t = a x + b`.

---

## Day 6 — What “Self‑Tuning” Really Means

**Goal:** Understand how models update themselves from fresh data using EMA‑style updates.

### 1. Why Self‑Tuning Is Needed

Buildings change:

- envelopes age  
- operators adjust sequences  
- schedules shift  
- night setbacks change  
- economizers get serviced (or broken)

A fixed model gets stale. A self‑tuning model incorporates **each new morning**.

### 2. Two Flavors of Self‑Tuning

**Type 1 — EMA on a Rate (Model 0)**

Model 0 keeps an EMA of the *rate*:

$$
\text{rate}_{new} = \alpha \cdot \text{rate}_{measured} + (1 - \alpha) \cdot \text{rate}_{old}
$$

where:

- `\text{rate}_{measured} = \Delta T / \Delta t` for that morning  
- α is a small learning factor (e.g. 0.05–0.20)

**Type 2 — EMA on Coefficients (Model 1 & 3)**

For a coefficient like a:

$$
a_{new} = (1 - \alpha)a_{old} + \alpha a_{today}
$$

Same for b (and d for Model 3). You blend old and new values.

### 3. Example: EMA Update (Model 0)

OldRate = 0.20°F/min  
MeasuredRate = 0.15°F/min  
α = 0.10

$$
\text{rate}_{new} = 0.10(0.15) + 0.90(0.20) = 0.015 + 0.18 = 0.195
$$

The model updates to a *slightly slower* rate (0.195).

### 4. Example: Coefficient Update (Model 1)

Old:

- a_old = 1.1  
- b_old = 8.0  

Today’s regression solution:

- a_today = 1.5  
- b_today = 6.0  

α = 0.10.

Update:

$$
\begin{aligned}
a_{new} &= 0.90(1.1) + 0.10(1.5) = 1.14 \\
b_{new} &= 0.90(8.0) + 0.10(6.0) = 7.8
\end{aligned}
$$

New model:

$$
t = 1.14 x + 7.8
$$

### 5. Micro‑Exercise (Single‑Point Update)

- Start temp = 62°F  
- End temp / SP = 72°F  
- So ΔT = 10°F  
- Actual warm‑up time = 72 min  

Old model:

- a_old = 0.85  
- b_old = 12  

Let α = 0.12.

1. Compute `x = (\Delta T)^2 = 100`.  
2. Compute predicted time: `t_{pred} = 0.85 \cdot 100 + 12`.  
3. Compute today’s implied slope:

   $$
   a_{today} = \frac{t_{actual}}{x} = \frac{72}{100} = 0.72
   $$

4. Update:

   $$
   a_{new} = 0.88 \cdot 0.85 + 0.12 \cdot 0.72
   $$

   (since 1 − 0.12 = 0.88)  
   and keep `b_{new} = b_{old}` for this single‑point update.

---

## Day 7 — Reading Warm‑Up Data Like a Model (Week 1 Review)

**Goal:** Learn to look at a small warm‑up dataset and decide if linear, quadratic, or weather‑based modeling is appropriate.

### 1. Example Warm‑Up Dataset

Five winter mornings:

| Day | Start Temp (°F) | Setpoint (°F) | ΔT | Warm‑Up Time (min) |
|-----|-----------------|---------------|----|---------------------|
| 1   | 68              | 72            | 4  | 24                  |
| 2   | 66              | 72            | 6  | 33                  |
| 3   | 64              | 72            | 8  | 50                  |
| 4   | 70              | 72            | 2  | 15                  |
| 5   | 62              | 72            | 10 | 72                  |

### 2. Check Time per Degree

Compute:

$$
\frac{t}{\Delta T}
$$

for each day:

- Day 1: 24/4 = 6.0 min/°F  
- Day 2: 33/6 ≈ 5.5 min/°F  
- Day 3: 50/8 ≈ 6.25 min/°F  
- Day 4: 15/2 = 7.5 min/°F  
- Day 5: 72/10 = 7.2 min/°F  

The “minutes per degree” is not constant → hints that simple linear might be okay but not perfect.

### 3. Look at ΔT²

Compute x = (ΔT)²:

| Day | ΔT | x = ΔT² | t (min) |
|-----|----|---------|---------|
| 1   | 4  | 16      | 24      |
| 2   | 6  | 36      | 33      |
| 3   | 8  | 64      | 50      |
| 4   | 2  | 4       | 15      |
| 5   | 10 | 100     | 72      |

As x goes 4 → 16 → 36 → 64 → 100, t grows in a roughly smooth, slightly accelerating way. That’s exactly what Model 1 is designed to capture.

### 4. Where Weather Might Matter

If you add outdoor temperatures:

- Cold mornings with similar ΔT but longer warm‑up → suggests OAT is influencing things.  
- Model 3 adds the `\Delta T \cdot WF` term to represent that.

### 5. Micro‑Exercise

Use this smaller table:

| Day | ΔT | Time (min) |
|-----|----|------------|
| A   | 3  | 18         |
| B   | 5  | 26         |
| C   | 8  | 60         |

1. Compute `t / \Delta T` for each day.  
2. Decide whether a linear model seems reasonable or whether the 8°F/60 min point looks disproportionately large (curving up).  
3. In words, say whether you’d start with Model 0, 1, or 3 for this site.

---

## Day 8 — What an EMA Actually Is

**Goal:** Develop strong intuition for EMA and see it as “smooth updating” rather than abstract math.

### 1. EMA Definition

The exponential moving average update:

$$
EMA_{new} = EMA_{old} + \alpha(x - EMA_{old})
$$

where:

- x = new observation  
- α = smoothing factor (0 < α ≤ 1)

### 2. HVAC Interpretation

For Model 0:

- x = measured °F/min for today’s warm‑up  
- EMA_old = yesterday’s learned rate  
- EMA_new = updated rateDegPerMin in Niagara

### 3. Behavior vs α

- α small (0.05) → very smooth, slow to change  
- α big (0.5) → very reactive, noisy

### 4. Micro‑Exercise

Let α = 0.2 and start with EMA = 0.15:

- x₁ = 0.25  
- x₂ = 0.05  
- x₃ = 0.18  

Update step by step and watch how EMA moves.

---

## Day 9 — Compute an EMA by Hand

**Goal:** Get comfortable doing a few EMA steps manually.

### 1. Example Sequence

Let α = 0.3, initial EMA₀ = 0.20.  
Measurements:

- Day 1: 0.24  
- Day 2: 0.18  
- Day 3: 0.22  

Update:

$$
EMA_{1} = EMA_{0} + 0.3(x_1 - EMA_{0})
$$

Repeat for days 2 and 3.

### 2. Micro‑Exercise

Pick α = 0.1 and initial EMA₀ = 0.18.  
Measurements:

- 0.30  
- 0.16  
- 0.20  

Compute EMA₁, EMA₂, EMA₃.

---

## Day 10 — How Niagara’s Optimal Start Uses EMA

**Goal:** Connect the theory to how Niagara actually stores and updates rateDegPerMin.

### 1. Observed Rate

Each successful warm‑up gives:

$$
\text{observedRate} = \frac{\Delta T}{\Delta t}
$$

Niagara then updates:

$$
rate_{new} = rate_{old} + \alpha (\text{observedRate} - rate_{old})
$$

### 2. Micro‑Exercise

Given rate_old = 0.21, α = 0.15, and an observed rate of 0.27:

1. Compute rate_new.  
2. Decide in words if the building is warming faster or slower than the model assumed.

---

## Day 11 — EMA vs Raw Average

**Goal:** Understand why EMA is preferred for warm‑up instead of a simple average.

### 1. Simple Average

Average of n observations:

$$
\bar{x} = \frac{1}{n}\sum_{i=1}^{n} x_i
$$

- Gives equal weight to all mornings, even 3 months ago.

### 2. EMA Advantages

- Recent mornings have more influence.  
- Doesn’t require storing the entire history.  
- Naturally forgets very old behavior.

### 3. Micro‑Exercise

You have 10 mornings of data.  
Discuss which is better for a live BAS model:

- Simple average of all 10  
- EMA with α = 0.1  

Explain your choice in 2–3 sentences.

---

## Day 12 — EMA as a Control “Gain”

**Goal:** Think of α like a tuning knob.

### 1. α as Learning Rate

- α too small → model changes too slowly.  
- α too large → model might oscillate.

### 2. Simple Thought Experiment

If α = 1, then:

$$
EMA_{new} = x
$$

You throw away all history and trust only today.

If α = 0, then:

$$
EMA_{new} = EMA_{old}
$$

You ignore today completely.

### 3. Micro‑Exercise

Explain in plain language:

- What happens if you pick α = 0.8 for a very noisy building.  
- What happens if you pick α = 0.02 for a building that just had major retro‑commissioning.

---

## Day 13 — Double EMA (EMA of EMA)

**Goal:** Understand the idea of smoothing an already smoothed signal.

### 1. Concept

You can define:

- EMA_fast with larger α  
- EMA_slow with smaller α  

This is more relevant to advanced analytics, but the idea is:

- Fast EMA reacts quickly.  
- Slow EMA tracks long‑term trend.

### 2. Micro‑Exercise

With α_fast = 0.4 and α_slow = 0.1, describe:

- Which one reacts faster to a sudden change in building behavior?  
- Which one should you trust more for “typical behavior”?

---

## Day 14 — Week 2 Review

**Goal:** Consolidate EMA intuition.

### 1. Recap

You should now be able to:

- Compute an EMA by hand for a short sequence.  
- Explain how Niagara uses EMA for Model 0.  
- Interpret α as a learning rate.

### 2. Micro‑Exercise

Write down in your own words (3–5 sentences) what EMA is doing in an optimal start context and why it’s a good fit for BAS.

---

## Day 15 — PNNL Model 0 (Pure Linear EMA Model)

**Goal:** Connect EMA and linear warm‑up prediction in a full Model 0 loop.

### 1. Model 0 Equation

$$
t_{opt} = \frac{\Delta T}{rate_{EMA}}
$$

### 2. Daily Cycle

1. Measure ΔT and actual warm‑up time.  
2. Compute observedRate = ΔT / time.  
3. Update rate_EMA.  
4. Use updated rate_EMA for tomorrow’s prediction.

### 3. Micro‑Exercise

Given:

- ΔT = 6°F, rate_EMA = 0.20°F/min  

Predict warm‑up time. Then imagine tomorrow’s observed rate is 0.24°F/min and α = 0.1 → update rate_EMA.

---

## Day 16 — PNNL Model 1 (Quadratic Algebraic Tuning)

**Goal:** Connect your quadratic algebra skills to the Model 1 structure.

### 1. Model 1 Equation

$$
t_{opt} = a(\Delta T)^2 + b
$$

Coefficients a, b are learned from warm‑up datapoints (x, t) with x = (ΔT)².

### 2. Micro‑Exercise

Given two datapoints:

- ΔT = 4°F → t = 24 min  
- ΔT = 8°F → t = 52 min  

1. Compute x = (ΔT)².  
2. Solve for a, b.  
3. Predict t for ΔT = 6°F.

---

## Day 17 — Solve Model 1 by Hand (3 Datapoints)

**Goal:** Practice regression for Model 1 with more than two datapoints.

### 1. Data

Assume:

- ΔT = 3°F → 18 min  
- ΔT = 5°F → 32 min  
- ΔT = 7°F → 54 min  

Compute x = (ΔT)² for all three. Use any two pairs for a,b and check the third.

### 2. Micro‑Exercise

After solving a and b, plug ΔT = 7°F into your model and compare against 54 min. Are you close?

---

## Day 18 — PNNL Model 3 Structure

**Goal:** Understand the warm‑up + weather idea.

### 1. Model 3 Equation

One common formulation:

$$
t = a(\Delta T) + b(\Delta T \cdot WF) + d
$$

where WF is some function of setpoint and outdoor air temperature, e.g.:

$$
WF = \frac{T_{set} - T_{oat}}{60}
$$

### 2. Interpretation

- a term → baseline ΔT effect.  
- b term → extra cost when it’s cold outside.  
- d → fixed overhead.

### 3. Micro‑Exercise

Given ΔT = 6°F, WF = 0.5, a = 3, b = 4, d = 10:

Compute predicted t.

---

## Day 19 — Solve Model 3 Coefficients by Hand (Conceptual)

**Goal:** See how three datapoints give you a, b, d.

### 1. Datapoints

For three mornings (i = 1,2,3):

- known: ΔTᵢ, WFᵢ, tᵢ  
- x₁ᵢ = ΔTᵢ  
- x₂ᵢ = ΔTᵢ·WFᵢ  

Set up:

$$
t_i = a x_{1i} + b x_{2i} + d
$$

This yields three equations in three unknowns.

### 2. Micro‑Exercise

Write out the three equations symbolically for generic ΔT₁,ΔT₂,ΔT₃, WF₁,WF₂,WF₃, t₁,t₂,t₃.

---

## Day 20 — How Niagara Stores the Coefficients

**Goal:** Map the abstract math to real slots/fields you’d see in a ProgramObject.

### 1. Typical Storage

- Model 0: `rateDegPerMin` (EMA result)  
- Model 1: `coefA`, `coefB`  
- Model 3: `coefA`, `coefB`, `offsetD`

### 2. Micro‑Exercise

In your own words, describe what each coefficient “means” physically in a building.

---

## Day 21 — Compare Linear vs Quadratic vs Weather Models

**Goal:** Learn to choose a model based on how a site behaves.

### 1. Quick Rules of Thumb

- Model 0: mild climates, small ΔT, simple systems.  
- Model 1: larger ΔT variation, interior zones, consistent envelope.  
- Model 3: strong weather sensitivity, exterior zones, cold climates.

### 2. Micro‑Exercise

Given a site where morning ΔT ranges from 1–12°F and runtime balloons on cold mornings, which model would you test first, and why?

---

## Day 22 — Building an Optimal Start Dataset

**Goal:** Understand what data you need to train these models.

### 1. Essential Fields

Each morning:

- Date / time  
- Zone start temp  
- Setpoint  
- Outdoor air temp  
- Time to reach setpoint (minutes)

### 2. Micro‑Exercise

Sketch a CSV header row that would store all necessary fields for training Model 3.

---

## Day 23 — Implement Model 0, 1, 3 in Barebones Python

**Goal:** Write very small Python functions for each model using only basic math.

### 1. Example Stubs

- Model 0: `predict_t_model0(delta_T, rate_ema)`  
- Model 1: `predict_t_model1(delta_T, a, b)`  
- Model 3: `predict_t_model3(delta_T, wf, a, b, d)`

### 2. Micro‑Exercise

Write and test these three functions in a simple Python script or notebook with a few fake numbers.

---

## Day 24 — Practice Solving Small Linear Systems

**Goal:** Get faster and more confident with 2×2 and 3×3 systems.

### 1. Practice Problems

Solve:

- 2×2:  
  `18 = 3k + c`, `30 = 5k + c`  
- 3×3: small, made‑up Model 3 system.

### 2. Micro‑Exercise

Time yourself solving a 2×2 system by hand. Try to get comfortable doing it in under a minute.

---

## Day 25 — Implement Full Model Evaluation Logic

**Goal:** Given a morning’s conditions and coefficients, compute predicted start time.

### 1. Inputs

- Zone start temp  
- Setpoint  
- OAT  
- Coefficients for chosen model  
- Optional: maximum pre‑start window, safety caps

### 2. Micro‑Exercise

Write a Python function:

```python
def compute_optimal_start_minutes(model_type, tz, tsp, oat, coeffs):
    ...
```

that branches on `model_type` and calls the right formulas.

---

## Day 26 — Implement Self‑Tuning Update Logic

**Goal:** Build the update step that consumes real data and adjusts the model.

### 1. Steps

1. After warm‑up, compute ΔT and actual minutes.  
2. For Model 0, compute observed rate and update EMA.  
3. For Model 1/3, recompute a_today, b_today (and d_today) then blend with α.

### 2. Micro‑Exercise

Draft pseudocode that takes a single morning’s data and outputs updated coefficients.

---

## Day 27 — Compare Model Accuracy on Fake/Historical Data

**Goal:** See differences in prediction error across models.

### 1. Simple Approach

- Pick 10 fake mornings.  
- Run Model 0, 1, 3 to predict minutes.  
- Compare predicted vs actual (error = predicted − actual).

### 2. Micro‑Exercise

Define an error metric you like (e.g. mean absolute error) and use it to compare the three models on your fake dataset.

---

## Day 28 — Pathological Cases in Real BAS Data

**Goal:** Recognize data that should be ignored or handled specially.

### 1. Tricky Situations

- ΔT ≈ 0 but long runtime (bad sensor, overshoot).  
- Negative ΔT (zone already above SP).  
- Extremely long or short warm‑up outliers.  
- Faulty equipment affecting one or two points.

### 2. Micro‑Exercise

List 3 rules you would enforce before letting a datapoint update your model.

---

## Day 29 — Design Your Own Hybrid Model

**Goal:** Think beyond PNNL and sketch your own twist.

### 1. Examples

- Linear Model 0 + small weather factor.  
- Quadratic Model 1 + EMA on top.  
- Separate models for weekdays vs weekends.

### 2. Micro‑Exercise

Write a short paragraph describing a hybrid model you’d like to try in a real BAS and why.

---

## Day 30 — Mini Optimal Start Engine (Capstone)

**Goal:** Conceptually put it all together.

### 1. Conceptual Pipeline

1. Ingest 10+ mornings of data (ΔT, OAT, minutes).  
2. Fit Model 0, 1, 3.  
3. For a new morning, predict optimal start using each model.  
4. After the run, update each model with new data.  
5. Track their performance over time.

### 2. Micro‑Exercise

Sketch a high‑level flowchart or bullet list of how your “mini optimal start engine” would operate over a 2‑week period in a real building.

---

All lessons and examples here are intended to be **BAS‑friendly**: you should be able to translate them directly into Niagara ProgramObjects, Python scripts, or any other control platform you work with.

Happy tuning. 🧠🔥🌡️
