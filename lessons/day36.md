# Day 36 — The Monday Morning Problem Defined

**Goal:** Understand why models struggle on Mondays

## 1. Concept and Definitions

The PNNL paper observed that all models performed poorly on Mondays
【913477360246089†L40-L46】.  After a weekend shutdown the building is
much colder than during the week; the thermal mass loses more heat.
Using recent history (Tuesday–Friday) under‑predicts the warm‑up time,
leading to comfort complaints.  This lesson defines the problem and
prepares you to address it.

## 2. How to Use It

Apply the concepts above using the formula or algorithm provided. Refer to the mini examples below for a demonstration.

## 3. Why This Matters

Understanding this concept allows you to build more accurate and efficient optimal‑start models, improving comfort and energy savings.

## 4. Mini‑Examples

Here's a simple Python demonstration:

```python
# Illustrate the Monday effect with sample data
week_rates = {'Tue':0.20, 'Wed':0.22, 'Thu':0.21, 'Fri':0.19}
monday_rate = 0.12  # much slower after weekend
avg_week_rate = sum(week_rates.values()) / len(week_rates)
delta_t = 6.0
t_week = delta_t / avg_week_rate
t_mon = delta_t / monday_rate
print(f'Using weekday rate → time={t_week:.1f} min')
print(f'Actual Monday rate → time={t_mon:.1f} min')
```

## 5. Micro‑Exercises

1. Compare Monday warm‑up times to those during the rest of the week in your own data.
2. Why do buildings cool down more over the weekend?
3. List factors that could exacerbate the Monday effect (e.g., heavy mass, cold weather).
4. Create a simple Python file that performs the calculations from this lesson.
   Use only basic variables, arithmetic, print statements and at most a `for` loop over a list. Avoid defining functions or using `zip`.
   Hint: replicate the structure of the examples above but use your own numbers or dataset.

## 6. Key Takeaway

Weekday history underestimates Monday warm‑up because the building cools for a longer period.  Recognising this issue is the first step toward fixing it.
