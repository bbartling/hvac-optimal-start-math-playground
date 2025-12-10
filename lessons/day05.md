# Day 5 — Tuning the Alpha (α)

**Goal:** Explore how the smoothing factor influences the EMA

## 1. Concept and Definitions

The smoothing factor α controls how much weight you give to the latest
observation relative to the historical average.  A small α (e.g., 0.1)
means the estimate changes slowly, while a large α (e.g., 0.9) almost
follows the current data point.  Choosing α is a trade‑off between
responsiveness and stability.  Too small and the model adapts too
slowly to seasonal changes; too large and the estimate becomes noisy.
You can visualise this by updating an EMA with the same sequence
using different α values.

## 2. How to Use It

Apply the concepts above using the formula or algorithm provided. Refer to the mini examples below for a demonstration.

## 3. Why This Matters

Understanding this concept allows you to build more accurate and efficient optimal‑start models, improving comfort and energy savings.

## 4. Mini‑Examples

Here's a simple Python demonstration:

```python
# Compare EMAs with different alpha values
observations = [0.2, 0.25, 0.18, 0.22, 0.19]
for alpha in [0.1, 0.5, 0.9]:
    ema = observations[0]
    for obs in observations[1:]:
        ema = ema + alpha * (obs - ema)
    print(f'Final EMA with α={alpha} → {ema:.3f} °F/min')
```

## 5. Micro‑Exercises

1. Using the code above, try adding an extreme observation (e.g., 0.35 °F/min).  How do the EMAs change?
2. What happens if α=0?  What happens if α=1?
3. Suggest how to pick α for a slowly changing building versus a rapidly changing one.
4. Create a simple Python file that performs the calculations from this lesson.
   Use only basic variables, arithmetic, print statements and at most a `for` loop over a list. Avoid defining functions or using `zip`.
   Hint: replicate the structure of the examples above but use your own numbers or dataset.

## 6. Key Takeaway

Tuning α requires balancing fast adaptation against sensitivity to noise.  Moderate values (0.1–0.3) often work well for HVAC.
