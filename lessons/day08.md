# Day 8 — What an EMA Actually Is

**Goal:** Understand the definition of an exponential moving average (EMA) and why it’s perfect for self‑tuning.

An EMA is a running average that gives more weight to recent observations.  It updates with a simple one‑line formula:

```
EMA_new = EMA_old + alpha * (value − EMA_old)
```

Where `alpha` (0 < α ≤ 1) controls how quickly the average responds.  A small α smooths out noise; a large α reacts quickly.

## Key Concepts

* **Recency:** Newer datapoints influence the EMA more than older ones.
* **Smoothing factor:** α close to 0 makes the EMA slow to change; α close to 1 makes it nearly equal to the latest value.
* **No history needed:** You don’t store a long list of values — just the current EMA.

## Mini‑Exercises

1. Suppose the current EMA is 10 and α = 0.2.  Compute the new EMA if the next value is 14.
2. What happens to the EMA if α = 0.05 and the next value jumps by 10?  Does the average move a lot or a little?

## Key Takeaway

An EMA is a memory‑efficient way to track trends.  It’s ideal for Model 0 because it adjusts the degrees‑per‑minute rate gradually as new mornings are observed.
