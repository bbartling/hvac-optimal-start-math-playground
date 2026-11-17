"""Synthetic zones with known physics, used by several tests."""
import math

from hvac_optimal import RecoveryEvent


def exp_recovery(start, target, tau_min, mode="heat", step=5.0, horizon=360.0, oat=20.0,
                 post_weekend=False, t_inf=None):
    """Zone approaching t_inf exponentially (time constant tau); returns a RecoveryEvent."""
    if t_inf is None:
        t_inf = target + (3.0 if mode == "heat" else -3.0)
    traj, reached, t = [], None, 0.0
    while t <= horizon:
        temp = t_inf + (start - t_inf) * math.exp(-t / tau_min)
        traj.append((t, temp))
        ok = temp >= target if mode == "heat" else temp <= target
        if ok and reached is None:
            reached = t
            break
        t += step
    return RecoveryEvent(mode, start, target, oat, reached, tuple(traj), post_weekend, oat)


def linear_recovery(start, target, min_per_deg, mode="heat", step=5.0, oat=20.0,
                    post_weekend=False):
    sign = 1.0 if mode == "heat" else -1.0
    d = abs(target - start)
    total = d * min_per_deg
    traj, t = [], 0.0
    while t < total:
        traj.append((t, start + sign * t / min_per_deg))
        t += step
    traj.append((total, target))
    return RecoveryEvent(mode, start, target, oat, total, tuple(traj), post_weekend, oat)
