


"""
Given α₃,a=1.8, α₃,b=2.2 and α₃,d=4.0, compute t for ΔT=6°F and WF=0.5.
"""

T_sp = 70.0
zone_temp = 70.0
oat = 9.0

WF = (T_sp - oat) / 60.0
delta_t = T_sp - zone_temp
feature = delta_t * WF


print(f'Weather factor WF = {WF:.2f}')
print(f'ΔT × WF        = {feature:.2f}')


# Compute Model 3 prediction with sample coefficients
alpha_a, alpha_b, alpha_d = 1.8, 2.2, 4.0
t_pred = alpha_a * delta_t + alpha_b * (delta_t * WF) + alpha_d
print(f'Predicted time = {t_pred:.1f} minutes')