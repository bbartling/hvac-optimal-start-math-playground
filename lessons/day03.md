# Day 3 — The Noise Problem

**Goal:** Recognise that a single day’s rate can be misleading

## 1. Concept and Definitions

Real buildings rarely warm at exactly the same speed every day.  Weather,
occupancy, and equipment variations cause the observed rate to bounce
around.  Using only today’s rate may lead to large errors, because the
measurement is noisy.  Instead, controllers smooth the rate over many days
to avoid jitter and overreaction.

You can simulate noise by adding random fluctuations to a ‘true’ rate and
see how the predicted time varies.

## 2. How to Use It

Apply the concepts above using the formula or algorithm provided. Refer to the mini examples below for a demonstration.

## 3. Why This Matters

Understanding this concept allows you to build more accurate and efficient optimal‑start models, improving comfort and energy savings.

## 4. Mini‑Examples

Here's a simple Python demonstration:

```python
import random
true_rate = 0.2  # °F/min
noisy_rates = [true_rate + random.uniform(-0.05, 0.05) for _ in range(5)]
delta_t = 5.0
for i, r in enumerate(noisy_rates, 1):
    t_est = delta_t / r
    print(f'Day {i}: rate={r:.3f} → t≈{t_est:.1f} min')
```

## 5. Micro‑Exercises

1. Run the script several times.  How much does the predicted time change?
2. Why might yesterday’s warm‑up rate be different from today’s?
3. Describe two factors that could cause noisy warm‑up data in buildings.
4. Create a simple Python file that performs the calculations from this lesson.
   Use only basic variables, arithmetic, print statements and at most a `for` loop over a list. Avoid defining functions or using `zip`.
   Hint: replicate the structure of the examples above but use your own numbers or dataset.

## 6. Key Takeaway

Relying on a single noisy measurement leads to unpredictable predictions.  Smoothing the rate over time reduces this noise.
