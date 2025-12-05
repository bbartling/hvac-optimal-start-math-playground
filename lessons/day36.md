# Day 36 — The “Monday Morning” Problem Defined

**Goal:** Describe why all models tend to underpredict runtime on Mondays and what causes the discrepancy.

## 1.  What Happens Over the Weekend

During a typical work week, buildings cool down for only 12–16 hours overnight.  On Monday morning, however, the building has been off for 48+ hours.  Walls, floors and furnishings have “cold soaked” far beyond the normal nightly setback.  

When you plug Monday’s ΔT into any of the previous models, they see only the temperature difference — they don’t know the building mass is colder **inside**.  As a result, the predicted warm‑up time is too short.

## 2.  The Evidence from PNNL

Researchers at PNNL observed that all four models underestimated Monday warm‑up time by 20–60 minutes【508931384575534†L420-L456】.  They recommended either adding a fixed time adder or scaling the prediction by a “cold soak” factor on Mondays.

## 3.  Micro‑Exercises

1. Look at a week of your own data.  Compare Monday’s actual warm‑up time to Tuesday’s for the same ΔT.  
2. Compute the ratio `actual_monday / predicted_monday` for each model and see how big the error is.  
3. Discuss in a few sentences why the models fail to capture the weekend effect.

## 4.  Key Takeaway

The Monday problem is real and must be addressed separately; ignoring it leads to cold occupants and wasted energy.
