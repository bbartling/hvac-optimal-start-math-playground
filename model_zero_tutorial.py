"""
Ultra-dumb linear model with EMA learning.
Identical to what the Niagara optimal start ProgramObject does,
but shown with the simplest Python possible.

Niagara logic:
    minutesPredicted = deltaT / rateEMA

After a real warmup run:
    observedRate = deltaT / actualMinutes
    rateEMA = rateEMA + emaStep * (observedRate - rateEMA)
"""

# ---------------------------------------------
# 1. Initial "learned" rate (°F per minute)
# ---------------------------------------------
rateEMA = 0.10       # same as Niagara default starting estimate
emaStep = 0.30       # how fast the rate learns (0.0–1.0)

print("Starting rateEMA =", round(rateEMA, 3), "°F/min\n")

# ---------------------------------------------
# 2. Fake data for several days of warmup runs
#    Format: (zoneTempAtStart, setpoint, actualMinutes)
# ---------------------------------------------
runs = [
    (65, 72, 40),     # Day 1
    (68, 72, 25),     # Day 2
    (70, 72, 18),     # Day 3
]

# ---------------------------------------------
# 3. Predict function (same math as Niagara)
# ---------------------------------------------
def predictWarmup(zoneTemp, setpointTemp, rate):
    deltaT = abs(setpointTemp - zoneTemp)

    # Avoid divide by zero (Niagara also protects here)
    if rate <= 0.000001:
        return 0.0

    return deltaT / rate


# ---------------------------------------------
# 4. Run through each fake historical day
# ---------------------------------------------
for (zoneStart, sp, actualMin) in runs:

    print("==============================")
    print("Starting zoneTemp =", zoneStart, "°F")
    print("Setpoint =", sp, "°F")
    print("Actual warmup time =", actualMin, "minutes")

    # ------ Predict BEFORE learning ------
    predicted = predictWarmup(zoneStart, sp, rateEMA)
    print("Predicted warmup =", round(predicted, 1), "minutes")

    # ------ Compute actual observed rate ------
    deltaT = abs(sp - zoneStart)

    # If actualMin is zero or deltaT is zero → cannot learn
    if actualMin > 0 and deltaT > 0:
        observedRate = deltaT / actualMin
    else:
        observedRate = rateEMA     # fallback: no learning

    print("ObservedRate =", round(observedRate, 3), "°F/min")

    # ------ EMA update (Niagara does exactly this) ------
    oldRate = rateEMA
    rateEMA = oldRate + emaStep * (observedRate - oldRate)

    print("Old rateEMA =", round(oldRate, 3))
    print("New rateEMA =", round(rateEMA, 3), "\n")


# ---------------------------------------------
# 5. Predict tomorrow after learning
# ---------------------------------------------
print("==============================")
print("Tomorrow prediction:")

tomorrowZone = 66
tomorrowSetpoint = 72

minutesTomorrow = predictWarmup(tomorrowZone, tomorrowSetpoint, rateEMA)

print("Tomorrow zoneTemp =", tomorrowZone, "°F")
print("Final learned rateEMA =", round(rateEMA, 3), "°F/min")
print("Predicted warmup =", round(minutesTomorrow, 1), "minutes")
