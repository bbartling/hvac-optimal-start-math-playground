import math
from pathlib import Path

import pytest

from hvac_optimal.models import NativeMinutesPerDegree, PNNLModel4, TrainingReceipt
from hvac_optimal.replay import ResearchSelector, assess_event, load_recovery_events, run_replay


def event(identifier="1", *, date="2026-01-01", scenario="site/weather", ahu="ahu1", mode="heat",
          post_weekend=False, trace=((0, 65), (5, 67), (10, 70)), source_complete=True):
    return assess_event(dict(event=identifier, date=date, scenario=scenario, ahu=ahu, mode=mode,
                             post_weekend=post_weekend, start=trace[0][1], target=70 if mode == "heat" else 65,
                             oat=30, oat_mean=31, source_complete=source_complete, traj=trace), 1.0)


class PreviousDuration:
    def __init__(self, log=None, name="model", prior=0):
        self.log, self.name, self.value = log, name, prior

    def predict(self, *args):
        if self.log is not None:
            self.log.append(("predict", self.name, self.value))
        return self.value

    def update(self, observed):
        if self.log is not None:
            self.log.append(("update", self.name, observed["event"]))
        if observed["complete"]:
            self.value = observed["t"]
        return TrainingReceipt(self.name, observed["mode"], observed["complete"],
                               "observed" if observed["complete"] else "censored")


def test_prediction_precedes_all_training_and_date_order_is_stable():
    log = []
    factory = lambda: {name: PreviousDuration(log, name) for name in ("a", "b")}
    result = run_replay([event("2", date="2026-01-02"), event("1")], factory)
    assert log[:4] == [("predict", "a", 0), ("predict", "b", 0), ("update", "a", "1"), ("update", "b", "1")]
    assert [row["prediction"] for row in result.records] == [0, 0, 10, 10]


def test_future_outcome_cannot_change_an_earlier_prediction():
    first = event("1")
    a = run_replay([first, event("2", date="2026-01-02")], lambda: {"x": PreviousDuration()})
    b = run_replay([first, event("2", date="2026-01-02", trace=((0, 65), (100, 70)))],
                   lambda: {"x": PreviousDuration()})
    assert a.records[0]["prediction"] == b.records[0]["prediction"]


def test_models_reset_per_scenario_and_ahu():
    rows = [event("1"), event("2", date="2026-01-02"), event("3", ahu="ahu2"), event("4", scenario="other/weather")]
    result = run_replay(rows, lambda: {"x": PreviousDuration()})
    predictions = {row["event"]: row["prediction"] for row in result.records}
    assert predictions == {"1": 0, "2": 10, "3": 0, "4": 0}


def test_one_endpoint_for_every_model_keeps_original_censoring_visible():
    e = event(source_complete=False, trace=((0, 65), (5, 69.2), (10, 69.5)))
    assert e["t"] == 5 and e["complete"] and not e["source_complete"]
    assert e["traj"] == ((0.0, 65.0), (5.0, 69.2))
    assert e["endpoint_time_method"] == "first_observed_sample_within_tolerance"
    result = run_replay([e], lambda: {"x": PreviousDuration()})
    assert result.summary()[0]["source_censored"] == 1
    assert result.summary()[0]["endpoint_censored"] == 0


def test_partial_is_not_a_full_target_time_but_can_train_partial_estimators():
    partial = event(source_complete=False, trace=((0, 65), (5, 65.001)))
    assert partial["t"] is None and partial["status"] == "partial"
    result = run_replay([partial], lambda: {"native": NativeMinutesPerDegree(), "decay": PNNLModel4()})
    assert all(row["actual"] is None and row["error"] is None for row in result.records)
    assert all(row["training"]["accepted"] for row in result.records)
    assert all(row["training"]["details"]["complete"] is False for row in result.records)


def test_at_endpoint_counts_as_observed_zero_without_fake_training_duration():
    e = event(trace=((0, 69.5), (5, 70)))
    assert e["t"] == 0 and e["status"] == "at_endpoint"
    result = run_replay([e], lambda: {"x": PreviousDuration()})
    assert result.records[0]["actual"] == 0
    assert result.summary()[0]["at_endpoint"] == 1


def test_no_prediction_imputation_and_common_cohort_is_explicit():
    result = run_replay([event("1"), event("2", date="2026-01-02")],
                        lambda: {"ready": PreviousDuration(), "untrained": PreviousDuration(prior=None)})
    summaries = {row["model"]: row for row in result.summary()}
    assert result.records[1]["prediction"] is None
    assert summaries["ready"]["assessed"] == 2
    assert summaries["untrained"]["assessed"] == 1
    assert summaries["ready"]["common_assessed"] == summaries["untrained"]["common_assessed"] == 1
    assert summaries["untrained"]["unassessed"] == 1


def test_clamp_is_opt_in_and_keeps_raw_prediction():
    factory = lambda: {"x": PreviousDuration(prior=1000)}
    assert run_replay([event()], factory).records[0]["prediction"] == 1000
    row = run_replay([event()], factory, max_lead=180).records[0]
    assert row["prediction"] == 180 and row["raw_prediction"] == 1000 and row["max_lead"] == 180


def test_selector_only_uses_prior_common_errors_separated_by_mode_and_weekend():
    selector = ResearchSelector(window=8)
    rows = [event("1"), event("2", date="2026-01-02"), event("3", date="2026-01-03", post_weekend=True),
            event("4", date="2026-01-04", mode="cool", trace=((0, 70), (5, 65)))]
    result = run_replay(rows, lambda: {"a": PreviousDuration(prior=10), "b": PreviousDuration(prior=20)}, selector=selector)
    selections = result.selection_records
    assert [row["model"] for row in selections] == [None, "a", None, None]
    assert selections[1]["prior_mae"] == {"a": 0, "b": 10}
    assert selections[1]["prior_counts"] == {"a": 1, "b": 1}


def test_callback_sees_decision_before_current_outcome_and_is_copy_isolated():
    messages = []
    def callback(message):
        messages.append(message.copy())
        message["phase"] = "mutated"
    result = run_replay([event()], lambda: {"x": PreviousDuration()}, callback=callback,
                        selector=ResearchSelector(cold_start_model="x"))
    assert [row["phase"] for row in messages] == ["prediction", "selection", "outcome", "training"]
    assert "actual" not in messages[1]
    assert result.selection_records[0]["actual"] == 10


def test_invalid_trace_is_visible_and_never_trains():
    malformed = event(trace=((0, 65), (5, 67), (4, 68)))
    log = []
    result = run_replay([malformed], lambda: {"x": PreviousDuration(log)})
    assert log == []
    assert result.summary()[0]["invalid"] == 1
    assert result.records[0]["training"]["reason"] == "invalid_event"


def test_tolerance_mismatch_is_rejected():
    with pytest.raises(ValueError, match="tolerances"):
        run_replay([event()], lambda: {"x": NativeMinutesPerDegree(allowable_deviation=0)})


def test_bundled_replay_keeps_all_events_and_reports_censoring():
    events = load_recovery_events(Path(__file__).parents[1] / "data")
    assert len(events) == 1163
    assert sum(not row["source_complete"] for row in events) == 130
    assert sum(row["complete"] for row in events) == 1090
    assert sum(row["status"] == "invalid" for row in events) == 0
    result = run_replay(events)
    assert len(result.records) == 1163 * 8
    summaries = result.summary()
    assert all(row["events"] == 1163 and row["endpoint_censored"] == 73 for row in summaries)
    assert len({row["common_assessed"] for row in summaries}) == 1
    assert all(row["mae"] is None or math.isfinite(row["mae"]) for row in summaries)
