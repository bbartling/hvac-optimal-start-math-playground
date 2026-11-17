import pytest

from hvac_optimal import (CoastSample, FirstOrderCoast, OptimalStartPlanner, OptimalStopPlanner,
                          ZoneReading, make_stop_model)

from helpers import linear_recovery


def zones(*temps, heat=70.0, cool=75.0):
    return [ZoneReading(f"z{i}", t, heat, cool) for i, t in enumerate(temps)]


def test_zone_reading_modes():
    assert ZoneReading("a", 65, 70, 75).mode() == "heat"
    assert ZoneReading("a", 78, 70, 75).mode() == "cool"
    assert ZoneReading("a", 72, 70, 75).mode() is None
    assert ZoneReading("a", 65, 70, 75).deficit() == 5


def test_untrained_planner_uses_max_lead():
    p = OptimalStartPlanner("pnnl_m1_quadratic", max_lead=180)
    assert p.lead_minutes(zones(60.0), oat=20.0) == 180


def test_all_zones_in_band_means_no_start():
    p = OptimalStartPlanner()
    assert p.lead_minutes(zones(72.0, 73.0), oat=50.0) == 0.0
    assert not p.should_start(5, zones(72.0), oat=50.0)


def test_worst_zone_decides_and_clamp():
    p = OptimalStartPlanner("m0_linear_ema", max_lead=180, min_lead=10)
    for z in ("z0", "z1"):
        p.learn(z, linear_recovery(64.0, 70.0, 10.0))
    lead = p.lead_minutes(zones(69.0, 64.0), oat=20.0)
    single = p.lead_minutes(zones(64.0), oat=20.0)
    assert lead == pytest.approx(single)
    assert p.lead_minutes(zones(69.9), oat=20.0) >= 10.0
    assert p.lead_minutes(zones(20.0), oat=20.0) == 180.0


def test_should_start_timing():
    p = OptimalStartPlanner("fixed_90")
    assert not p.should_start(120, zones(60.0), oat=10.0)
    assert p.should_start(85, zones(60.0), oat=10.0)


def test_nonrecovering_zone_is_excluded():
    p = OptimalStartPlanner("m0_linear_ema")
    for z in ("z0", "z1"):
        p.learn(z, linear_recovery(66.0, 70.0, 10.0))
    for _ in range(2):
        p.record_outcome("z1", False)
    assert "z1" in p.nonrecovering()
    # z1 is 15 deg cold but capacity limited: it must not pin the start
    assert p.lead_minutes(zones(66.0, 55.0), oat=0.0) < 100
    # if every zone is flagged the planner falls back to all zones
    p.record_outcome("z0", False)
    p.record_outcome("z0", False)
    assert p.lead_minutes(zones(66.0, 55.0), oat=0.0) > 100


def test_group_mode_one_model():
    p = OptimalStartPlanner.recommended()
    assert p.group
    p.learn("ahu1", linear_recovery(64.0, 70.0, 10.0))
    p.learn("ahu1", linear_recovery(64.0, 70.0, 10.0))
    assert len(p.models) == 1
    assert p.lead_minutes(zones(64.0, 69.0, 66.0), oat=20.0) > 0


def _trained_coast(rate=-0.5, n=40, occupied=False):
    m = FirstOrderCoast()
    for _ in range(n):
        m.update(CoastSample(72.0, 72.0 + rate * 0.5, 50.0, 30.0, occupied))
    return m


def test_stop_needs_history():
    p = OptimalStopPlanner()
    assert not p.should_stop(30, zones(72.5), oat=50.0)


def test_stop_when_drift_is_small_and_not_when_large():
    slow = OptimalStopPlanner(lambda: _trained_coast(-0.2))
    for z in ("z0",):
        slow.model_for(z)
    assert slow.should_stop(30, zones(72.5), oat=50.0)
    assert not slow.should_stop(30, zones(70.7), oat=50.0)  # too close to the heating edge
    fast = OptimalStopPlanner(lambda: _trained_coast(-6.0))
    assert not fast.should_stop(60, zones(72.5), oat=50.0)


def test_stop_window_limits():
    p = OptimalStopPlanner(lambda: _trained_coast(-0.1), max_early=60)
    assert not p.should_stop(90, zones(72.5), oat=50.0)
    assert not p.should_stop(0, zones(72.5), oat=50.0)


def test_no_early_stop_never_stops():
    p = OptimalStopPlanner("no_early_stop")
    assert not p.should_stop(30, zones(72.5), oat=50.0)


def test_restart_guard():
    p = OptimalStopPlanner(restart_guard=0.27)
    assert p.should_restart(zones(70.2))
    assert p.should_restart(zones(74.8))
    assert not p.should_restart(zones(72.5))


def test_first_order_coast_learns_physics():
    """Recover a and b of dT/dt = a (OAT - T) + b from noise-free samples."""
    a_true, b_true = 0.08, 0.5
    m = FirstOrderCoast(lam=1.0)
    for i in range(200):
        t0 = 65.0 + (i % 10)
        oat = 20.0 + 3 * (i % 7)
        m.update(CoastSample(t0, t0 + (a_true * (oat - t0) + b_true) * 0.25, oat, 15.0))
    a, b, _ = m.rls.theta
    assert a == pytest.approx(a_true, rel=0.05)
    assert b == pytest.approx(b_true, abs=0.2)


def test_union_bounds_are_wider_without_occupied_history():
    g = make_stop_model("first_order_coast")
    u = make_stop_model("first_order_coast_union")
    for m in (g, u):
        for _ in range(40):
            m.update(CoastSample(72.0, 71.8, 40.0, 30.0, False))
    lo_g, hi_g = g.bounds(72.0, 40.0, 60.0, True)
    lo_u, hi_u = u.bounds(72.0, 40.0, 60.0, True)
    assert lo_u <= lo_g and hi_u >= hi_g - 1e-9


def test_arrival_feedback_moves_aim_inside_band():
    p = OptimalStartPlanner("m0_linear_ema", group=True, arrival_feedback=True, fb_step=0.5, fb_q=0.8)
    p.learn("g", linear_recovery(66.0, 70.0, 10.0))
    in_band = zones(70.3)
    assert p.lead_minutes(in_band, oat=20.0) == 0.0
    for _ in range(4):
        p.record_arrival(1.5)        # short by 1.5 F at occupancy, four days running
    assert p.offset == pytest.approx(1.6)
    assert p.lead_minutes(in_band, oat=20.0) > 0.0
    for _ in range(100):
        p.record_arrival(0.0)        # on time: the offset decays back toward zero
    assert p.offset == 0.0


def test_arrival_feedback_converges_to_target_quantile():
    import random
    rng = random.Random(3)
    p = OptimalStartPlanner("fixed_60", group=True, arrival_feedback=True, fb_step=0.1, fb_q=0.8)
    late = 0
    for day in range(4000):
        need = rng.gauss(1.0, 0.5)   # degrees of extra aim the day would have needed
        is_late = need > p.offset
        p.record_arrival(1.0 if is_late else 0.0)
        if day >= 1000:
            late += is_late
    assert late / 3000 == pytest.approx(0.2, abs=0.04)
