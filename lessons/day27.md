# Day 27 — Tuning Model 3

**Goal:** Discuss how to select the history length and learning weights for Model 3 to balance responsiveness and stability.

## 1. History Window

PNNL suggests using at least 10 days of data to fit Model 3.  Fewer points risk overfitting; more points slow adaptation.

## 2. Learning Weights

After each new day, blend the new coefficients into the old ones using a small weight (e.g., 0.1), just like Model 1 tuning.

## 3. Practical Tip

Maintain a rolling buffer of (ΔT, WF, minutes) tuples.  Each morning, drop the oldest and add the newest before fitting.

## 4. Key Takeaway

Proper tuning makes Model 3 both smart and stable.  Too little data yields noise; too much data makes it sluggish.
