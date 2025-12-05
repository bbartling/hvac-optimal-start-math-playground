# Day 38 — The “Technician’s Guess”

**Goal:** Introduce the simple but surprisingly effective practice of adding a fixed buffer time on Mondays.

## 1.  The Rule of Thumb

Many operators simply add 60 minutes to the predicted start time on Mondays.  For example, if Model 3 says “Start 90 minutes early,” the technician will set it to 150 minutes.  This heuristic recognises that mathematical models under‑predict the weekend cold soak.

## 2.  When It Works

Fixed adders work reasonably well when the building and weather conditions are consistent week over week.  They are easy to implement on any BAS without advanced math.

## 3.  Limitations

* If the weekend was unseasonably warm or cold, the fixed adder may be too high or too low.  
* Larger buildings with variable schedules may need more sophisticated scaling.

## 4.  Micro‑Exercises

1. Compare the technician’s guess to actual Monday warm‑up times over 5 weeks.  How often is it within ±10 minutes?  
2. Try different fixed adders (30, 45, 60 minutes) and compute the mean absolute error for each.  
3. Brainstorm scenarios where a fixed adder fails badly (e.g., holiday weekends, extreme weather).

## 5.  Key Takeaway

A simple fixed time adder can dramatically improve comfort on Mondays, but it is only a blunt instrument.
