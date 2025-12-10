# Day 16 — The Reference Temperature (T_ref)

**Goal:** Choose an appropriate baseline for the weather ratio

## 1. Concept and Definitions

The ratio in Model 2 uses a reference outdoor temperature T_ref.  According
to the PNNL paper, T_ref is set to 0 °C (32 °F) for heating and 37.78 °C
(100 °F) for cooling【913477360246089†L514-L554】.  T_ref represents a
"worst‑case" condition where the equipment must run continuously.  The
ratio is calculated as (T_ref − OAT_yesterday)/(T_ref − OAT_today).
Choosing an appropriate T_ref ensures the ratio scales the runtime
correctly.

## 2. How to Use It

Apply the concepts above using the formula or algorithm provided. Refer to the mini examples below for a demonstration.

## 3. Why This Matters

Understanding this concept allows you to build more accurate and efficient optimal‑start models, improving comfort and energy savings.

## 4. Mini‑Examples

Here's a simple Python demonstration:

```python
# Compute the ratio for heating mode using T_ref=32°F
T_ref = 32.0
oat_prev = 20.0
oat_curr = 15.0
ratio = (T_ref - oat_prev) / (T_ref - oat_curr)
print(f'Heating ratio = {ratio:.2f}')

# Compute the ratio for cooling mode using T_ref=100°F
T_ref_cool = 100.0
oat_prev = 85.0
oat_curr = 90.0
ratio_cool = (T_ref_cool - oat_prev) / (T_ref_cool - oat_curr)
print(f'Cooling ratio = {ratio_cool:.2f}')
```

## 5. Micro‑Exercises

1. Why is the ratio >1 when today is colder than yesterday (heating mode)?
2. How would you pick T_ref for a climate with very mild winters?
3. What happens if today’s outdoor temperature equals T_ref?
4. Create a simple Python file that performs the calculations from this lesson.
   Use only basic variables, arithmetic, print statements and at most a `for` loop over a list. Avoid defining functions or using `zip`.
   Hint: replicate the structure of the examples above but use your own numbers or dataset.

## 6. Key Takeaway

T_ref anchors the weather ratio.  Selecting an appropriate value based on heating or cooling mode ensures the ratio scales runtimes realistically.
