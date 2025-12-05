# Day 32 — The “Coast to Stop” Effect

**Goal:** Discuss why Model 4 is well‑suited for systems that slow down near the end of the warm‑up.

## 1. Non‑linear Progress

Many RTUs and heat pumps deliver a lot of heat initially, then throttle back as the zone approaches setpoint to avoid overshooting.  This produces an exponential decay in the error.

## 2. Model Fit

A logarithmic model naturally captures this “coasting” behaviour.  Quadratic or linear models may overshoot or underestimate the last few minutes.

## 3. Key Takeaway

If your system coasts into the setpoint, try Model 4.  It better represents decaying progress.
