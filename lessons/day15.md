# Day 15 — Why Indoor Temp isn’t Enough

**Goal:** Recognise that outdoor conditions affect warm‑up

## 1. Concept and Definitions

For perimeter zones exposed to the weather, indoor temperature alone
doesn’t capture how quickly a space will warm.  Cold outdoor air can
continue to steal heat during warm‑up, slowing the response.  Model 2
introduces an outdoor temperature adjustment to compensate for this
effect【913477360246089†L514-L554】.

## 2. How to Use It

Apply the concepts above using the formula or algorithm provided. Refer to the mini examples below for a demonstration.

## 3. Why This Matters

Understanding this concept allows you to build more accurate and efficient optimal‑start models, improving comfort and energy savings.

## 4. Mini‑Examples

Here's a simple Python demonstration:

```python
# Demonstrate how colder outdoor air increases predicted time
delta_t = 6.0
base_rate = 0.20  # °F/min
t_base = delta_t / base_rate
for diff in [0, -10, -20]:
    # diff is the drop in outdoor temperature compared to yesterday (°F)
    ratio = (100 - (70 + diff)) / (100 - 70)  # using T_ref=100°F as in cooling mode
    t_adj = t_base * ratio
    print(f'Outdoor drop={diff:+}°F → ratio={ratio:.2f}, time={t_adj:.1f} min')
```

## 5. Micro‑Exercises

1. Explain why colder outdoor conditions result in a ratio greater than 1.
2. What happens if today is warmer than yesterday?
3. Which zones (interior or perimeter) benefit most from Model 2?
4. Create a simple Python file that performs the calculations from this lesson.
   Use only basic variables, arithmetic, print statements and at most a `for` loop over a list. Avoid defining functions or using `zip`.
   Hint: replicate the structure of the examples above but use your own numbers or dataset.

## 6. Key Takeaway

Outdoor air temperature can significantly alter warm‑up time.  Model 2 corrects the base runtime using a weather‑dependent ratio.
