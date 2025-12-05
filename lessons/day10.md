# Day 10 — The Slope Coefficient (a)

**Goal:** Understand the meaning of the quadratic coefficient a and how it relates to a zone’s thermal “heaviness.”

## 1. What Is `a`?

In `t = a * (DeltaT)^2 + b`, the **slope coefficient** `a` determines how quickly time grows as ΔT increases.

* **Small `a` (e.g., 0.3):** Warm‑up grows slowly with ΔT.
* **Large `a` (e.g., 1.0):** Warm‑up grows quickly — the zone is “heavy.”

## 2. Estimating `a`

You can estimate `a` by plotting historical ΔT² against warm‑up time and fitting a line.  The slope of that line is `a`.

## 3. Example

Given these pairs `(DeltaT, t)`:

| ΔT | t (min) |
|---|---------|
| 3 | 14 |
| 5 | 30 |
| 8 | 65 |

Compute `a` using two points:

```
x1, y1 = 3**2, 14
x2, y2 = 5**2, 30
a = (y2 - y1) / (x2 - x1)
# a ≈ 16 / 16 = 1.0
```

## 4. Key Takeaway

The `a` coefficient reflects thermal inertia: higher `a` → heavier zone → longer warm‑up per degree.
