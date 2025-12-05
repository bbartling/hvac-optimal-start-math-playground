# Day 22 — The Missing Link: Weather Factor (WF)

**Goal:** Introduce the weather factor used in Model 3 and show how to compute it.

## 1. Defining WF

In Model 3, we define the **weather factor** as:

```
WF = (T_setpoint - T_oat) / 60
```

dividing by 60 normalises the term so that a 30 °F difference yields WF = 0.5.

## 2. Why Normalise?

Without scaling, the outdoor term could dominate the regression.  Dividing by a constant keeps coefficients in a reasonable range.

## 3. Key Takeaway

WF ties together the indoor and outdoor temperatures, giving the model a second feature to work with.
