# Day 14 — Week 2 Review

**Goal:** Consolidate everything you learned about exponential moving averages and smoothing over the past week.

By the end of Week 2 you have:

* Defined what an EMA is and why it’s used in BAS.
* Practised computing EMAs by hand with different α values.
* Seen how Niagara’s Model 0 uses an EMA to track the heating or cooling rate.
* Compared EMAs to raw averages and understood the role of the smoothing factor as a control gain.
* Explored advanced smoothing with double EMAs.

Take a moment to reflect on how these pieces fit together.  The EMA is the heart of Model 0 and influences the slope in Models 1 and 3.  Choosing α appropriately keeps your optimal‑start times sensible even as the building and weather change.

## Mini‑Exercise

Write a short note (2–3 sentences) to yourself explaining:

* Why you can’t just use a raw average for degrees‑per‑minute.
* What happens if you set α too high or too low.
* How a double EMA differs from a single EMA.

## Key Takeaway

Week 2 equips you with the smoothing tools needed to make self‑tuning robust.  EMAs keep models adaptive yet stable and underpin every optimal‑start algorithm you’ll build going forward.