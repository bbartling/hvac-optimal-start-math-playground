# Day 38 — The Technician’s Guess

**Goal:** Introduce the industry practice of adding a fixed buffer to Monday start times.

## 1. The Rule of Thumb

A common strategy: **add 60 minutes** to whatever the model predicts for Monday.  It’s crude but often effective.

## 2. Implementation

In code you might do:

```python
predicted = model3_prediction  # or whichever model
if is_monday:
    predicted += 60
```

## 3. Discussion

This ignores nuance but prevents occupant discomfort.  It’s a good first step until more data is available.

## 4. Key Takeaway

Sometimes a human guess outperforms math.  Don’t be afraid to combine intuition and analytics.
