# Day 4 — Intro to Exponential Moving Average (EMA)

**Goal:** Learn how smoothing stabilises the rate estimate

## 1. Concept and Definitions

To tame the noise seen in daily rate measurements, controllers use an
exponential moving average (EMA).  An EMA takes a fraction (α) of the
difference between the current observation and the previous estimate and
adds it to the old value.  Investopedia describes the general formula for
EMAs as "EMA = current × multiplier + previous EMA × (1 − multiplier)".  For HVAC warm‑up rates this can be
written as:

    new_rate = old_rate + α × (observed_rate − old_rate)

The smoothing factor α (between 0 and 1) determines how quickly the
estimate adapts to new data.  Small α leads to slow changes; large α reacts
quickly but may overreact to noise.

## 2. How to Use It

Apply the concepts above using the formula or algorithm provided. Refer to the mini examples below for a demonstration.

## 3. Why This Matters

Understanding this concept allows you to build more accurate and efficient optimal‑start models, improving comfort and energy savings.

## 4. Mini‑Examples

Here's a simple Python demonstration:

```python
# Update an EMA of the warm‑up rate
alpha = 0.3
old_rate = 0.20
observed_rate = 0.25
new_rate = old_rate + alpha * (observed_rate - old_rate)
print(f'Old rate     = {old_rate:.2f} °F/min')
print(f'Observed rate = {observed_rate:.2f} °F/min')
print(f'Updated EMA  = {new_rate:.2f} °F/min')
```

## 5. Micro‑Exercises

1. Starting from a rate of 0.20 °F/min, update the EMA with observed rates of 0.18, 0.22 and 0.16 using α=0.2.
2. Explain how the choice of α affects the balance between responsiveness and stability.
3. Where else are EMAs used in engineering or finance?
4. Create a simple Python file that performs the calculations from this lesson.
   Use only basic variables, arithmetic, print statements and at most a `for` loop over a list. Avoid defining functions or using `zip`.
   Hint: replicate the structure of the examples above but use your own numbers or dataset.

## 6. Key Takeaway

An exponential moving average blends new observations with history, smoothing out random fluctuations in the data.
