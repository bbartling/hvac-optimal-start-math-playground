# Day 29 — Build Your Own Hybrid Model

**Goal:** Design a custom optimal‑start model that combines elements of Models 0, 1 and 3 to suit your specific site.

The PNNL models provide great starting points, but real buildings vary.  Today you think creatively about combining linear, quadratic and weather terms to build a hybrid model.

## 1.  Identify Your Building’s Behaviour

* Does it warm nearly linearly up to a certain ΔT and then slow down?  You might blend Model 0 and Model 1.
* Does outdoor temperature matter only when it’s below 40 °F?  You could weight the weather factor term only when WF exceeds a threshold.
* Are there different heating stages (e.g. heat pump vs resistance heat)?  Consider separate coefficients for each stage.

## 2.  Example Hybrid Form

Here’s one possible hybrid:

```
t_predicted = (DeltaT / rateEMA)                     # linear part
             + c1 * max(0, (DeltaT − DeltaT_threshold))
             + c2 * (DeltaT * WF)
```

Where `c1` adds extra minutes once ΔT exceeds a chosen threshold and `c2` accounts for weather.  You can tune `rateEMA`, `c1` and `c2` separately.

## 3.  Training and Tuning

* Use the EMA update for `rateEMA` as usual.
* Fit `c1` and `c2` using regression on the subset of datapoints where their terms are active.
* Blend updates with α to smooth them.

## Mini‑Exercises

1. Sketch a hybrid formula that is linear when ΔT < 5 °F and quadratic when ΔT ≥ 5 °F.
2. Propose how you would detect a threshold for when weather becomes significant and incorporate that into your model.
3. Write pseudo‑code for updating your custom coefficients alongside the EMA.

## Key Takeaway

Optimal‑start modelling is not one‑size‑fits‑all.  Once you understand the building blocks — EMA, linear slopes, quadratics, weather factors — you can mix them to build a model tailored to your site.  Just remember to keep it interpretable and to validate it with data.