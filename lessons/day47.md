# Day 47 — Feature Engineering (Data Prep)

**Goal:** Prepare your HVAC data so a simple math engine can solve complex logic like "Mondays."

## 1. Normalization

Math engines hate big numbers (like 5,000) mixed with small numbers (like 1). They get confused because the weights for the big numbers have to be tiny, while weights for small numbers have to be huge.
* **Rule:** Scale your inputs to be between 0 and 1.
* **Action:** Divide your $\Delta T$ by the maximum expected $\Delta T$ (e.g., 20°F).

## 2. One-Hot Encoding (The Monday Flag)

How do we tell math about "Monday"? We can't multiply the word "Monday" by a weight.
We create a **Binary Flag**:
* Is_Monday = 1.0
* Is_Monday = 0.0 (Tuesday–Sunday)

## 3. The Input Vector

Our input `X` is no longer just one number. It is a list (vector):
`Input = [Scaled_DeltaT, Is_Monday_Flag]`

The model will learn a separate weight for each item in this list.
* Weight 1 learns "How much time per degree?"
* Weight 2 learns "How much EXTRA time for Monday?"

## 4. Micro‑Exercises

1.  Take a raw dataset: `[Monday, 10°F diff], [Tuesday, 5°F diff]`.
2.  Convert it to a numerical matrix assuming max $\Delta T = 20$.
    * Row 1: `[0.5, 1.0]`
    * Row 2: `[0.25, 0.0]`
3.  Write a small Python list-comprehension to automate this scaling.

## 5. Key Takeaway

Garbage In, Garbage Out. Good AI is 80% data preparation and 20% math.
