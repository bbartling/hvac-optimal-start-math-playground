# Day 9 — Compute an EMA by Hand

**Goal:** Practise calculating exponential moving averages yourself and see how α changes the smoothing.

On Day 8 you learned the EMA formula.  Today you’ll compute a few by hand to build intuition.

## Step‑by‑Step Example

Assume α = 0.3 and an initial EMA of 20.  You record these values over four days: 18, 25, 22, 17.  Compute the EMA after each value:

1. **First value (18):**
   
   `EMA_1 = 20 + 0.3 * (18 − 20) = 20 − 0.6 = 19.4`

2. **Second value (25):**
   
   `EMA_2 = 19.4 + 0.3 * (25 − 19.4) ≈ 19.4 + 1.68 = 21.08`

3. **Third value (22):**
   
   `EMA_3 = 21.08 + 0.3 * (22 − 21.08) ≈ 21.08 + 0.276 = 21.356`

4. **Fourth value (17):**
   
   `EMA_4 = 21.356 + 0.3 * (17 − 21.356) ≈ 21.356 − 1.307 = 20.049`

Notice how the EMA reacts to changes but doesn’t jump as much as the raw values do.

## Mini‑Exercises

1. Using α = 0.1 and an initial EMA of 15, compute the EMA after the sequence: 16, 14, 20.
2. Using α = 0.5 (a fast learner) and an initial EMA of 30, update the EMA after the values: 35 and then 25.

## Key Takeaway

Manually computing EMAs shows how each new value nudges the average.  The weight α decides whether the model learns quickly or slowly.