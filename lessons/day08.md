# Day 8 — Why Heat Transfer Isn’t Linear

**Goal:** Understand why heating slows down as the zone gets closer to setpoint and introduce the quadratic form.

## 1. The Physics of Thermal Mass

Real buildings don’t heat uniformly.  The first few degrees warm quickly; the last few creep slowly as the walls, furniture, and air exchange soak up heat.

## 2. Introducing the Quadratic Model

To capture this behavior, **Model 1** uses:

```
t = a * (DeltaT)^2 + b
```

* `a` controls the curvature (higher means more slowdown).  
* `b` represents the “dead time” or baseline minutes before temperature starts to move.

## 3. Example

Suppose `a = 0.6` and `b = 5`.
* ΔT = 2 °F → `t = 0.6 * 4 + 5 = 7.4 min`
* ΔT = 8 °F → `t = 0.6 * 64 + 5 = 43.4 min`

Notice how time grows faster than ΔT.

## 4. Key Takeaway

The quadratic model acknowledges that heating gets harder as the room warms.  This is more realistic than a straight line for many interior zones.
