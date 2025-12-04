# Day 4 — Systems of Equations Refresher (Foundation of Model 3)

**Goal:** Get comfortable solving for two or three unknowns using multiple equations.

Day 4 bridges the gap between linear and weather‑adjusted models.  Both Model 1 and Model 3 rely on solving small systems of equations to determine their coefficients.  This day demystifies those steps.

## 1.  Why Systems Matter in Optimal Start

* **Model 1** has two unknowns (`a` and `b`) in the form `t = a*(DeltaT)^2 + b`.  Two datapoints give you two equations to solve.
* **Model 3** has three unknowns (`a`, `b`, `d`):

```
t = a*(DeltaT) + b*(DeltaT * WF) + d
```

Three datapoints give you three equations to solve.  This is the classic 3×3 linear system.

## 2.  Example: 2×2 System (Model 1 Style)

Given two warm‑up observations:

* x₁ = 9, t₁ = 16
* x₂ = 25, t₂ = 40  (where x = (DeltaT)²)

Solve for `a` and `b` in `t = a*x + b`:

```
a = (40 − 16) / (25 − 9) = 24 / 16 = 1.5
b = 16 − 1.5 * 9 = 16 − 13.5 = 2.5
```

Thus:

```
t = 1.5*x + 2.5
```

## 3.  Example: 3×3 System (Model 3 Style)

Model 3 uses two inputs per datapoint:

* x₁ = DeltaT
* x₂ = DeltaT × WF  (WF is the weather factor)

Each warm‑up morning provides one equation:

```
t_i = a * x1_i + b * x2_i + d
```

Collect three mornings → three equations → solve simultaneously for `a`, `b`, and `d`.  This can be done by hand (substitution/elimination) or with a small matrix solver.  Niagara’s ProgramObject does this under the hood.

## 4.  Day 4 Micro‑Exercise

Solve this 2×2 system by hand:

```
14 = 4*a + b
26 = 8*a + b
```

Steps:

1. Subtract the first equation from the second to isolate `a`.
2. Plug `a` back into one of the equations to find `b`.
3. Write the resulting model `t = a*(DeltaT) + b`.

## 5.  Key Takeaway From Day 4

Small systems of equations are the engine behind the self‑tuning models.  Model 1 solves a 2×2 system; Model 3 solves a 3×3.  Once you’re comfortable subtracting one equation from another, you’re ready to implement both models in code or on paper.