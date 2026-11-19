"""Prevent invalid experimental comparisons from being labeled matched evidence."""
from copy import deepcopy

import pytest

from tools.summarize_simulation import summarize


def fixture():
    sampling = {"selected_zone_ids": ["room-x"], "fallback_reason": None}
    ahu = {"ahu_id": "arbitrary-ahu", "sampling": sampling,
           "native_learning_events": 3, "accepted_research_fits": 4,
           "metrics": {"candidate": {"assessed": 3, "unassessed": 1, "unsupported": 0,
                       "common_assessed": 3, "common_absolute_error_sum": 12.0}}}
    job = {"scenario": {"scenario_id": "b/weather", "building": "b"}, "policy": "native",
           "phase": "both", "seed": 0, "sample_fraction": .3, "zone_weights": None,
           "status": "complete", "steps": 8640, "steps_completed": 8640,
           "mean_reward": -.10, "simulator_recirculation_cap": .7, "ahus": [ahu]}
    other = deepcopy(job)
    other.update(policy="winner", mean_reward=-.12)
    return {"status": "complete", "failed": 0, "pending": 0, "job_count": 2,
            "signature": "fixture-not-an-executed-run", "results": [job, other]}


def test_reward_direction_and_evidence_counts():
    result = summarize(fixture())
    assert result["winner_better_scenarios"] == 0
    assert result["winner_worse_scenarios"] == 1
    assert result["ahu_runs"] == 2
    assert result["independent_scenario_ahu_pairs"] == 1
    assert result["ahu_ticks_total"] == 17280
    assert result["policies"]["native"]["shadow_metrics"]["candidate"]["common_mae_minutes"] == 4


@pytest.mark.parametrize("change", ["sample", "phase", "steps", "missing_arm", "common_cohort"])
def test_reject_unmatched_or_incomplete_experiment(change):
    data = fixture()
    job = data["results"][1]
    if change == "sample":
        job["ahus"][0]["sampling"]["selected_zone_ids"] = ["different-room"]
    elif change == "phase":
        job["phase"] = "start"
    elif change == "steps":
        job["steps_completed"] = 12
    elif change == "missing_arm":
        job["scenario"]["scenario_id"] = "b/other-weather"
    else:
        metric = deepcopy(job["ahus"][0]["metrics"]["candidate"])
        metric["common_assessed"] = 2
        job["ahus"][0]["metrics"]["another-candidate"] = metric
    with pytest.raises(ValueError):
        summarize(data)
