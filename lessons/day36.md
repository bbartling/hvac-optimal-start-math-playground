# Day 36 — The Monday Morning Problem Defined

**Goal:** Define why all models fail on Mondays and explore the concept of cold soak.

## 1. What Happens Over the Weekend

Buildings often shut off HVAC on Friday night.  By Monday morning, everything has cooled or heated far deeper than after a single night.  This is called **cold soak** (or heat soak in cooling season).

## 2. Why Models Fail

Model 0‑4 rely on recent data (Tuesday through Friday).  Monday behaves like a different system: longer, nonlinear recovery.  PNNL observed that all models underpredict Monday warm‑up【475518369320562†L420-L434】.

## 3. Key Takeaway

Mondays are special.  You need extra logic or manual intervention to avoid cold calls from occupants.
