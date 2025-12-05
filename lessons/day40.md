# Day 40 — Experiment: Separate Histories

**Goal:** Consider keeping a dedicated dataset for Monday runs and training a model specifically for that day.

## 1.  The Idea

Instead of forcing one model to fit both weekday and Monday data, you can maintain two histories: one for Tuesday–Friday, another for Monday.  You learn separate coefficients (or EMA rates) for each.  On Mondays you use the “Monday model,” on other days you use the normal model.

## 2.  Challenges

* You only get one Monday per week, so it takes 10 weeks to collect 10 data points.  
* Weather conditions can change dramatically week to week, making it hard to learn stable coefficients.

## 3.  Hybrid Approaches

Some practitioners use a small Monday dataset but still blend it with normal weekday data using a higher α value on Mondays.  Others maintain separate models but fall back to normal models when Monday data are scarce.

## 4.  Micro‑Exercises

1. Create two EMAs: one that updates on Tuesday–Friday, and one that updates only on Monday.  Compare their values after 12 weeks.  
2. Try fitting a simple linear regression to Monday data after 10 weeks.  How does it perform compared to using a cold soak multiplier?  
3. Describe the pros and cons of maintaining separate histories.

## 5.  Key Takeaway

Separate histories acknowledge the unique physics of Mondays but require patience and careful handling of sparse data.
