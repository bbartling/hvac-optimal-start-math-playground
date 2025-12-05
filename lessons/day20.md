# Day 20 — Sensitivity Check

**Goal:** Test how sensitive Model 2 is to changes in outdoor temperature and discuss potential pitfalls.

## 1. Sensitivity Analysis

Imagine yesterday’s OAT was 40 °F.  Evaluate the ratio for today at 30 °F, 20 °F, and 10 °F with `T_ref = 0 °F`.

* Today 30 °F: Ratio = (0 - 40) / (0 - 30) = 1.33
* Today 20 °F: Ratio = (0 - 40) / (0 - 20) = 2.0
* Today 10 °F: Ratio = (0 - 40) / (0 - 10) = 4.0

## 2. Discussion

Notice how quickly the ratio grows.  A 10 °F drop doubled the time; a 30 °F drop quadrupled it.  This may be too aggressive.

## 3. Mitigation

You can cap the ratio (e.g., max 2x) or blend outdoor and indoor predictions using Model 3.

## 4. Key Takeaway

Model 2 is powerful but can overreact.  Always test sensitivity before deploying.
