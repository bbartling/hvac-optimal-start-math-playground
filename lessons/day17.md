# Day 17 — The Ratio Formula

**Goal:** Derive the weather ratio used in Model 2 and illustrate how it scales the predicted time.

## 1. The Math

For heating season, the ratio is:

```
Ratio = (T_ref - T_oat_yesterday) / (T_ref - T_oat_today)
```

If today is colder than yesterday, the denominator is smaller → the ratio is greater than 1 → longer warm‑up.

## 2. Example

Yesterday OAT = 35 °F, Today OAT = 20 °F, `T_ref = 0 °F`:

```
Ratio = (0 - 35) / (0 - 20) = 35/20 = 1.75
```

So predicted time from indoor model is multiplied by 1.75.

## 3. Key Takeaway

The ratio stretches or shrinks the run time to reflect changing outdoor conditions.
