# Day 17 — The Ratio Formula

**Goal:** Apply the weather ratio to adjust the base runtime

## 1. Concept and Definitions

Model 2 multiplies the base warm‑up time by a ratio derived from outdoor
temperatures.  The formula is:

    ratio = (T_ref − OAT_yesterday) / (T_ref − OAT_today)

and the adjusted time is t_adj = t_base × ratio【913477360246089†L540-L554】.
If today is colder than yesterday the ratio exceeds 1, extending the
runtime; if today is warmer, the ratio shrinks the runtime.

## 2. How to Use It

Apply the concepts above using the formula or algorithm provided. Refer to the mini examples below for a demonstration.

## 3. Why This Matters

Understanding this concept allows you to build more accurate and efficient optimal‑start models, improving comfort and energy savings.

## 4. Mini‑Examples

Here's a simple Python demonstration:

```python
# Compute the adjusted runtime given base time and outdoor temperatures
t_base = 30.0
T_ref = 32.0
oat_prev, oat_curr = 25.0, 10.0
ratio = (T_ref - oat_prev) / (T_ref - oat_curr)
adjusted = t_base * ratio
print(f'Ratio      = {ratio:.2f}')
print(f'Adjusted time = {adjusted:.1f} min')
```

## 5. Micro‑Exercises

1. For heating mode with T_ref=32°F, oat_prev=20°F and oat_curr=25°F, compute the ratio and adjusted time for t_base=40 min.
2. Describe a scenario where the ratio is exactly 1.0.  What does this mean physically?
3. Why does the ratio blow up as oat_curr approaches T_ref?
4. Create a simple Python file that performs the calculations from this lesson.
   Use only basic variables, arithmetic, print statements and at most a `for` loop over a list. Avoid defining functions or using `zip`.
   Hint: replicate the structure of the examples above but use your own numbers or dataset.

## 6. Key Takeaway

The weather ratio stretches or shrinks the base runtime depending on how today’s outdoor temperature compares to yesterday’s.
