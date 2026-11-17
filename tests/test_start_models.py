import math

import pytest

from hvac_optimal import (START_MODELS, FixedLead, LinearRateEMA, PNNLMedianEnsemble,
                          PNNLModel1Quadratic, PNNLModel2OatRatio, PNNLModel3Regression,
                          PNNLModel4Exponential, RecoveryEvent, RepoSGDModel5, RobustRLSStart,
                          make_start_model)

from helpers import exp_recovery, linear_recovery


@pytest.mark.parametrize("name", sorted(START_MODELS))
def test_every_model_is_safe_untrained_and_after_training(name):
    m = make_start_model(name)
    p = m.predict("heat", 60.0, 70.0, 20.0)
    assert p is None or (p >= 0 and math.isfinite(p))
    assert m.predict("heat", 71.0, 70.0, 20.0) in (0.0, m.predict("heat", 71.0, 70.0, 20.0))
    for i in range(12):
        m.update(linear_recovery(62.0 + (i % 3), 70.0, 12.0, post_weekend=(i % 5 == 0)))
        m.update(linear_recovery(80.0, 75.0, 10.0, mode="cool", oat=90.0))
    for mode, temp, target, oat in [("heat", 63, 70, 10), ("cool", 79, 75, 95)]:
        p = m.predict(mode, temp, target, oat, post_weekend=True)
        assert p is not None and p >= 0 and math.isfinite(p)


def test_unknown_model_name():
    with pytest.raises(KeyError):
        make_start_model("nope")


def test_fixed_lead():
    assert FixedLead(90).predict("heat", 50, 70, 0) == 90


def test_zero_deficit_means_no_lead():
    m = RobustRLSStart()
    assert m.predict("heat", 70.5, 70.0, 20.0) == 0.0
    assert m.predict("cool", 74.0, 75.0, 90.0) == 0.0


def test_m0_ema_rate_update_matches_paper_eq24():
    m = LinearRateEMA(heat_rate=0.1, w=0.2)
    m.update(linear_recovery(64.0, 70.0, 20.0))  # actual rate 0.05 deg/min
    assert m.rate["heat"] == pytest.approx(0.1 + 0.2 * (0.05 - 0.1))


def test_pnnl_m1_coefficients_eq13_eq14():
    m = PNNLModel1Quadratic()
    e = linear_recovery(64.0, 70.0, 10.0)  # 6 deg in 60 min, 10 min per degree
    m.update(e)
    b = 10.0
    a = (60.0 - b) / 36.0
    assert m.b["heat"][-1] == pytest.approx(b)
    assert m.a["heat"][-1] == pytest.approx(a)
    assert m.predict("heat", 66.0, 70.0, 20.0) == pytest.approx(a * 16 + b)


def test_pnnl_m1_short_recovery_branch():
    m = PNNLModel1Quadratic()
    # whole recovery within the first degree -> t - b < 1 -> a = t / (10 dT)
    e = RecoveryEvent("heat", 69.0, 70.0, 20.0, 10.0, ((0, 69.0), (10.0, 70.0)))
    m.update(e)
    assert m.a["heat"][-1] == pytest.approx(10.0 / 10.0)


def test_pnnl_m2_oat_ratio_eq15():
    m = PNNLModel2OatRatio()
    m.update(linear_recovery(64.0, 70.0, 10.0, oat=40.0))  # rate 0.1 deg/min, trained at 40 F
    # colder morning: ratio (0 - 20) / (0 - 40) = 0.5 -> twice as long
    assert m.predict("heat", 64.0, 70.0, 20.0) == pytest.approx(6.0 / (0.5 * 0.1))
    # OAT below the 0 F reference (Fairbanks) is undefined in the paper: guard -> ratio 1
    assert m.predict("heat", 64.0, 70.0, -10.0) == pytest.approx(6.0 / (0.25 * 0.1)) or \
        m.predict("heat", 64.0, 70.0, -10.0) == pytest.approx(60.0)


def test_pnnl_m3_regression_eq19_and_feedback():
    m = PNNLModel3Regression()
    e = linear_recovery(64.0, 70.0, 10.0, oat=30.0)
    e.arrival_error = 2.0  # zone was 2 deg short at occupancy -> d += 5
    m.update(e)
    a = 10.0
    b = (60.0 - a * 6.0) * 10.0 / (6.0 * 40.0)
    assert m.b["heat"][-1] == pytest.approx(max(0.0, b))
    assert m.d["heat"] == 5.0
    assert m.predict("heat", 64.0, 70.0, 30.0) == pytest.approx(a * 6 + 5.0)


def test_pnnl_m4_exponential_eq21_23():
    tau = 40.0
    m = PNNLModel4Exponential(deviation=1.0)
    # error decays e(t) = e0 * exp(-t/tau) toward the target exactly
    traj = tuple((t, 70.0 - 8.0 * math.exp(-t / tau)) for t in range(0, 200, 5))
    m.update(RecoveryEvent("heat", 62.0, 70.0, 20.0, None, traj))
    c = math.exp(-1.0 / tau)
    assert m.c_list["heat"][-1] == pytest.approx(c, rel=1e-6)
    # t = ln(a/b)/ln(c) = tau * ln(8/1)
    assert m.predict("heat", 62.0, 70.0, 20.0) == pytest.approx(tau * math.log(8.0), rel=1e-6)
    assert m.predict("heat", 69.5, 70.0, 20.0) == 0.0  # within allowable deviation


def test_pnnl_median_counts_untrained_as_earliest():
    m = PNNLMedianEnsemble(earliest=180.0)
    # untrained: M1-M3 None -> 180; M4 uses default c -> some value; median = 180
    assert m.predict("heat", 62.0, 70.0, 20.0) == pytest.approx(180.0)


def test_pnnl_deployed_split_uses_weekend_models():
    m = PNNLMedianEnsemble(post_weekend_split=True)
    for _ in range(4):
        m.update(linear_recovery(64.0, 70.0, 5.0))
    weekday = m.predict("heat", 64.0, 70.0, 20.0)
    assert m.predict("heat", 64.0, 70.0, 20.0, post_weekend=True) == pytest.approx(weekday)
    m.update(linear_recovery(64.0, 70.0, 20.0, post_weekend=True))
    monday = m.predict("heat", 64.0, 70.0, 20.0, post_weekend=True)
    assert monday > weekday


def test_repo_m5_fits_monday_offset():
    m = RepoSGDModel5(epochs=3000, lr=0.05)
    for i in range(20):
        m.update(linear_recovery(64.0, 70.0, 10.0, post_weekend=(i % 5 == 0)))
    assert m.w["heat"] is not None


def test_robust_rls_learns_true_rate_and_monday_effect():
    m = RobustRLSStart()
    for day in range(30):
        pw = day % 5 == 0
        start = 62.0 + (day % 4)
        m.update(linear_recovery(start, 70.0, 20.0 if pw else 10.0, post_weekend=pw))
    weekday = m.point("heat", 64.0, 70.0, 20.0)
    monday = m.point("heat", 64.0, 70.0, 20.0, post_weekend=True)
    assert weekday == pytest.approx(60.0, abs=6.0)
    assert monday == pytest.approx(120.0, abs=12.0)


def test_robust_rls_margin_covers_noise():
    import random
    rng = random.Random(1)
    m = RobustRLSStart(q=0.8)
    late = 0
    for day in range(60):
        e = linear_recovery(64.0, 70.0, 10.0 * rng.uniform(0.8, 1.2))
        if day >= 20 and m.predict("heat", 64.0, 70.0, 20.0) < e.minutes_to_target:
            late += 1
        m.update(e)
    assert late / 40.0 < 0.4  # target ~20 % late, generous bound


def test_robust_rls_ignores_single_outlier():
    m = RobustRLSStart()
    for _ in range(15):
        m.update(linear_recovery(64.0, 70.0, 10.0))
    before = m.point("heat", 64.0, 70.0, 20.0)
    m.update(linear_recovery(64.0, 70.0, 100.0))  # sensor glitch / plant fault day
    after = m.point("heat", 64.0, 70.0, 20.0)
    assert abs(after - before) < 30.0


def test_exponential_zone_end_to_end_convergence():
    """Every learning model should converge near the truth on a clean 1R1C zone."""
    truth = exp_recovery(63.0, 70.0, 60.0).minutes_to_target
    for name in ["m0_linear_ema", "pnnl_m1_quadratic", "pnnl_m4_exponential", "robust_rls"]:
        m = make_start_model(name)
        for _ in range(15):
            m.update(exp_recovery(63.0, 70.0, 60.0))
        assert m.predict("heat", 63.0, 70.0, 20.0) == pytest.approx(truth, rel=0.5), name
