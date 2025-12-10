# Day 6 — Simulating Model 0 (Paper & Pencil)

**Goal:** Manually apply the linear EMA to a few days of data

## 1. Concept and Definitions

Before coding, it helps to simulate Model 0 by hand.  Suppose you observe
daily warm‑up rates and update the EMA each day.  Start with an initial
guess and repeatedly apply the EMA update rule from Day 4.  This
exercise shows how the estimate converges over time.  You can perform the
same process in Python to check your calculations.

## 2. How to Use It

Apply the concepts above using the formula or algorithm provided. Refer to the mini examples below for a demonstration.

## 3. Why This Matters

Understanding this concept allows you to build more accurate and efficient optimal‑start models, improving comfort and energy savings.

## 4. Mini‑Examples

Here's a simple Python demonstration:

```python
# Simulate Model 0 over several days
alpha = 0.3
ema_rate = 0.20
observed_rates = [0.25, 0.18, 0.22, 0.21, 0.19]
for day, obs in enumerate(observed_rates, 1):
    ema_rate = ema_rate + alpha * (obs - ema_rate)
    print(f'Day {day}: observed={obs:.2f}, EMA={ema_rate:.3f}')

# Predict warm‑up time on day 5 for ΔT=6°F using the final EMA
delta_t = 6.0
t_pred = delta_t / ema_rate
print(f'Predicted warm‑up time ≈ {t_pred:.1f} min')
```

## 5. Micro‑Exercises

1. Use α=0.1 and the same observations.  How does the final EMA differ?
2. If the observed rate suddenly drops to 0.10 °F/min on day 6, how does it impact the EMA?
3. Why might you reset the EMA when major equipment changes occur?
4. Create a simple Python file that performs the calculations from this lesson.
   Use only basic variables, arithmetic, print statements and at most a `for` loop over a list. Avoid defining functions or using `zip`.
   Hint: replicate the structure of the examples above but use your own numbers or dataset.

## 6. Key Takeaway

Hand calculations reinforce how the EMA filters noisy rates.  The same algorithm can be encoded in any language or BAS platform.
