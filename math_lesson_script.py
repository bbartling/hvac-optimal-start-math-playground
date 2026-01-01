


import math


"""tau = 10.0  # time constant
time_values = [0, 5, 10, 20]
for t in time_values:
    fraction = 1 - math.exp(-t / tau)
    print(f't={t} min → fraction charged={fraction:.3f}')
"""


# decay_rate=0.85 and Deadband=0.5°F, compute t for ΔT=6°F
deadband = 0.5
delta_t = 6.0
decay_rate = 1.05


t_pred = math.log(deadband / delta_t) / math.log(decay_rate)
print(f'Predicted time = {t_pred:.1f} minutes')