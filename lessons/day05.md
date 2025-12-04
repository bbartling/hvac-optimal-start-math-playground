# Day 5 — Regression Without Statistics (Just Algebra)

**Goal:** Demystify regression in the context of optimal start.  See that it’s just algebraic curve fitting — no fancy statistics required.

Many people hear the word “regression” and think of calculus or statistical software.  In optimal start, **regression** simply means “solve for the coefficients that best fit the data.”  It is pure algebra.

## 1.  Why Regression ≠ Statistics for Optimal Start

Models 1 and 3 are fixed‑form equations.  To “train” them, you plug in your datapoints and solve for the unknown coefficients.  There is no random noise, no probability distribution — just a few linear equations:

* Model 1: `t = a*x + b`, where `x = (DeltaT)^2`
* Model 3: `t = a*x1 + b*x2 + d`, where `x1 = DeltaT` and `x2 = DeltaT·WF`

Solving these is regression.  It is accomplished with subtraction and division, not statistics.

## 2.  Example of Algebraic Regression (Line Through Two Points)

Consider two quadratic datapoints (x, t):

```
(4, 10)
(25, 40)
```

Solve for `a` and `b` in `t = a*x + b`:

```
a = (40 − 10) / (25 − 4) = 30 / 21 ≈ 1.4286
b = 10 − 1.4286 * 4 ≈ 4.286
```

So the regression line is:

```
t ≈ 1.4286*x + 4.286
```

This is the unique line passing through both datapoints — nothing more mysterious than that.

## 3.  Interpreting Slopes and Intercepts

If the building warms faster, the slope (`a`) becomes smaller.  If the building has a big coil‑warm‑up lag, the intercept (`b`) grows.  Regression tells the story of the building in numbers.

## 4.  Day 5 Micro‑Exercise

Use the datapoints below to perform a hand regression:

| ΔT (°F) | x = (ΔT)² | t (min) |
|---------|----------|---------|
| 4       | 16       | 26      |
| 6       | 36       | 44      |

Steps:

1. Compute the slope `a`:
   
   `a = (44 − 26) / (36 − 16)`

2. Compute the intercept `b`:
   
   `b = 26 − a * 16`

3. Write the resulting model `t = a*x + b` and use it to predict the time for ΔT = 5 °F (x = 25).

## 5.  Key Takeaway From Day 5

Regression in the optimal‑start world is just algebra.  There’s no need for statistical software — you solve one or two linear equations by hand and then blend those coefficients over time.  That’s it.