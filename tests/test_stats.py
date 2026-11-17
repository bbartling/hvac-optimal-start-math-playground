import math
import random

import pytest

from hvac_optimal._stats import RLS, clamp, mad_scale, median, pnnl_ema, quantile


def reference_pnnl_ema(lst):
    """Verbatim logic of aems-edge manager/utils.py ema()."""
    s = 2.0 / (len(lst) + 1.0) * 2.0 if lst else 1.0
    s = s if s <= 1.0 else 1.0
    rev = lst[::-1]
    out = 0
    for n in range(len(lst)):
        out += rev[n] * s * (1.0 - s) ** n
    if rev:
        out += rev[-1] * (1.0 - s) ** len(lst)
    return out


@pytest.mark.parametrize("vals", [[5.0], [1.0, 2.0], [3, 1, 4], [3, 1, 4, 1, 5, 9, 2, 6]])
def test_pnnl_ema_matches_reference(vals):
    assert pnnl_ema(vals) == pytest.approx(reference_pnnl_ema(vals))


def test_pnnl_ema_short_lists_are_newest_value():
    assert pnnl_ema([10.0, 20.0, 30.0]) == pytest.approx(30.0)


def test_pnnl_ema_empty_raises():
    with pytest.raises(ValueError):
        pnnl_ema([])


def test_basic_stats():
    assert clamp(5, 0, 3) == 3 and clamp(-1, 0, 3) == 0
    assert median([3, 1, 2]) == 2 and median([1, 2, 3, 4]) == 2.5
    assert quantile([0, 10], 0.5) == 5
    assert mad_scale([1, 1, 1]) == 0


def test_rls_recovers_linear_model():
    rng = random.Random(0)
    r = RLS([0, 0], [1e3, 1e3], lam=1.0)
    for _ in range(200):
        x = rng.uniform(0, 10)
        r.update([x, 1.0], 3.0 * x + 7.0 + rng.gauss(0, 0.01))
    assert r.theta[0] == pytest.approx(3.0, abs=0.01)
    assert r.theta[1] == pytest.approx(7.0, abs=0.05)


def test_rls_forgetting_tracks_drift():
    r = RLS([0.0], [100.0], lam=0.9)
    for _ in range(50):
        r.update([1.0], 1.0)
    for _ in range(50):
        r.update([1.0], 5.0)
    assert r.theta[0] == pytest.approx(5.0, abs=0.05)
    assert all(math.isfinite(v) for row in r.P for v in row)
