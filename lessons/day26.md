# Day 26 — Handling Weird Coefficients

**Goal:** Explore why regression can produce negative or unexpected coefficients and how to mitigate.

## 1. Negative Coefficients?

Sometimes the regression finds `b < 0`, implying that colder weather makes heating faster.  That’s clearly wrong.

## 2. Causes

* Poor data quality or too few samples.
* Collinearity between features.
* Outliers (bad sensor readings).

## 3. Solutions

* Clamp `b` to zero if it goes negative.
* Increase the history window to include more data.
* Remove obvious outliers before fitting.

## 4. Key Takeaway

Regression is data‑driven.  Garbage in → garbage out.  Sanity‑check your coefficients.
