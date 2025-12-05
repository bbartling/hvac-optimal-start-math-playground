# Day 40 — Experiment: Separate Histories

**Goal:** Propose keeping a separate dataset for Mondays and discuss pros and cons.

## 1. Idea

Maintain two sets of coefficients: one trained on Tuesday–Friday data and one on Mondays.  On Monday, use the Monday model.

## 2. Pros

* Models the unique Monday behaviour.
* Avoids contaminating weekday model with Monday anomalies.

## 3. Cons

* Only one data point per week → slow learning.
* Monday behaviour itself may vary (holidays, varying setbacks).

## 4. Key Takeaway

Separate histories are theoretically appealing but practically limited by data scarcity.
