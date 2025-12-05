# Day 24 — Reinforce Solving Small Linear Systems

**Goal:** Become fluent in solving 2×2 and 3×3 linear systems by hand or with simple code.

Small systems of equations appear throughout optimal‑start tuning.  Today is pure practise — no new concepts, just drills.

## 1.  2×2 Systems (Model 1)

The general form is:

```
t1 = a*x1 + b
t2 = a*x2 + b
```

Subtract the first equation from the second to isolate `a`, then solve for `b`.

### Example Drill

Solve for `a` and `b`:

```
18 = a*9 + b
34 = a*25 + b
```

## 2.  3×3 Systems (Model 3)

General form:

```
t1 = a*x11 + b*x12 + d
t2 = a*x21 + b*x22 + d
t3 = a*x31 + b*x32 + d
```

Subtract one equation from the others to eliminate `d`, then solve the resulting 2×2 system for `a` and `b`, finally back‑solve for `d`.

### Example Drill

Solve for `a`, `b`, `d`:

```
30 = 5*a + 1.0*b + d
48 = 7*a + 2.0*b + d
70 = 9*a + 4.5*b + d
```

## 3.  Tools and Tips

* Use subtraction to eliminate variables one at a time.
* Keep track of decimals; consider multiplying both sides to clear fractions.
* If you write scripts, `numpy.linalg.solve` can solve systems quickly, but try it by hand to build intuition.

## Mini‑Exercises

1. Solve the 2×2 system:

   `12 = a*4 + b`  and `28 = a*9 + b`

2. Solve the 3×3 system:

   `22 = 3*a + 1.2*b + d`,
   `38 = 5*a + 2.5*b + d`,
   `55 = 7*a + 4.2*b + d`

3. Write a small Python function to solve any 2×2 linear system of the form:

   `t1 = a*x1 + b`,
   `t2 = a*x2 + b`

## Key Takeaway

Solving linear systems is a basic skill you’ll use repeatedly.  Practise until subtracting equations and back‑solving becomes automatic.  The faster you can solve these systems, the quicker you can diagnose and tune optimal‑start models.