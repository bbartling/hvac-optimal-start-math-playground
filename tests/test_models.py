"""Analytic estimator fixtures: hand calculations, cadence and visible rejections."""
import copy
import json
import math
from pathlib import Path
import subprocess
import sys
import unittest

from hvac_optimal.models import (
    G36RecoveryLearner, LinearRateEMA, NativeMinutesPerDegree,
    PNNLMedian, PNNLModel1, PNNLModel2, PNNLModel3, PNNLModel4,
    default_models, minutes_per_first_degree, pnnl_ema,
)


def recovery(mode="heat", duration=40.0, deviation=1.0, **changes):
    start = 65.0 if mode == "heat" else 75.0
    sign = 1 if mode == "heat" else -1
    endpoint = 70.0 - sign * deviation
    event = dict(mode=mode, start=start, target=70.0, oat=30.0 if mode == "heat" else 100.0,
                 oat_mean=30.0 if mode == "heat" else 100.0,
                 t=duration, complete=True, post_weekend=False, arrival_error=None,
                 traj=[(0.0, start), (5.0, start + sign), (duration, endpoint)])
    event.update(changes)
    return event


class PNNLAnalyticTests(unittest.TestCase):
    def test_ema_matches_expanded_source_weights(self):
        values = [1, 2, 3, 4, 5, 6, 7, 8]
        weight = 4 / 9
        expected = sum(value * weight * (1 - weight) ** i
                       for i, value in enumerate(reversed(values))) + values[0] * (1 - weight) ** 8
        self.assertAlmostEqual(pnnl_ema(values), expected)
        self.assertEqual(pnnl_ema([1, 100]), 100)
        with self.assertRaises(ValueError):
            pnnl_ema([])

    def test_first_degree_interpolates_adjacent_samples_with_jitter(self):
        event = recovery(traj=[(0, 65), (4, 65.5), (7, 66.5), (40, 69)])
        self.assertEqual(minutes_per_first_degree(event), 5.5)
        cool = recovery("cool", traj=[(0, 75), (4, 74.5), (7, 73.5), (40, 71)])
        self.assertEqual(minutes_per_first_degree(cool), 5.5)

    def test_johnson_literal_formula_and_common_endpoint_adaptation(self):
        # With deviation=0 the fit is the supplied Johnson algebra:
        # a=(40-5)/5^2=1.4, b=5, next identical prediction=40.
        literal = PNNLModel1(allowable_deviation=0)
        receipt = literal.update(recovery(deviation=0))
        self.assertTrue(receipt.accepted)
        self.assertEqual(receipt.parameters, {"a": 1.4, "b": 5.0})
        self.assertEqual(literal.predict("heat", 65, 70, 30), 40)
        # Common assessment endpoint is 69 F: gap=4 instead of 5.
        adapter = PNNLModel1(allowable_deviation=1)
        self.assertEqual(adapter.update(recovery()).parameters["a"], 35 / 16)
        self.assertEqual(adapter.predict("heat", 65, 70, 30), 40)
        self.assertEqual(adapter.predict("heat", 69, 70, 30), 0)

    def test_johnson_source_fallback_is_not_silently_replaced(self):
        model = PNNLModel1(allowable_deviation=0)
        event = recovery(duration=5, deviation=0, start=69, traj=[(0, 69), (5, 70)])
        receipt = model.update(event)
        self.assertEqual(receipt.parameters, {"a": 0.5, "b": 5.0})
        self.assertEqual(model.predict("heat", 69, 70, 30), 5.5)

    def test_carrier_ratio_both_directions_and_paper_reference_option(self):
        heating = PNNLModel2(allowable_deviation=0)
        heating.update(recovery(start=66, deviation=0, traj=[(0, 66), (40, 70)]))
        # rate=4/40=.1; current gap=5; (0-30)/(0-15)=2.
        self.assertEqual(heating.predict("heat", 65, 70, 15), 100)
        cooling = PNNLModel2(allowable_deviation=0)
        cooling.update(recovery("cool", start=74, deviation=0, oat=90, oat_mean=90,
                                traj=[(0, 74), (40, 70)]))
        self.assertEqual(cooling.predict("cool", 75, 70, 95), 100)
        paper_constant = PNNLModel2(allowable_deviation=0, oat_ref_heat=32)
        paper_constant.update(recovery(start=66, deviation=0, traj=[(0, 66), (40, 70)]))
        self.assertAlmostEqual(paper_constant.predict("heat", 65, 70, 15), 50 * 2 / 17)

    def test_carrier_singularities_are_reported_not_clipped(self):
        model = PNNLModel2()
        model.update(recovery())
        self.assertIsNone(model.predict("heat", 65, 70, 0))
        self.assertEqual(model.last_prediction_reason, "undefined_outdoor_ratio")
        self.assertIsNone(model.predict("heat", 65, 70, -5))
        self.assertEqual(model.last_prediction_reason, "invalid_model_prediction")
        trained_at_reference = PNNLModel2()
        trained_at_reference.update(recovery(oat=0, oat_mean=0))
        self.assertIsNone(trained_at_reference.predict("heat", 65, 70, 15))

    def test_siemens_preserves_supplied_heat_cool_asymmetry(self):
        model = PNNLModel3(allowable_deviation=0)
        heat = model.update(recovery(deviation=0, arrival_error=20))
        cool = model.update(recovery("cool", deviation=0, arrival_error=-20))
        # Heating a=first-degree time=5, b=(40-5*5)*10/(5*40)=.75.
        self.assertEqual(heat.parameters, {"a": 5.0, "b": 0.75, "adjust_time": 0.0})
        # Cooling a=whole-recovery time/gap=8, leaving b=0.
        self.assertEqual(cool.parameters, {"a": 8.0, "b": 0.0, "adjust_time": 0.0})
        self.assertFalse(heat.details["arrival_feedback_used"])
        self.assertFalse(cool.details["arrival_feedback_used"])
        self.assertEqual(model.predict("heat", 65, 70, 30), 40)
        self.assertEqual(model.predict("cool", 75, 70, 100), 40)
        self.assertEqual(model.adjust_time, 0)

    def test_siemens_rejects_undefined_weather_fit_with_receipt(self):
        model = PNNLModel3()
        receipt = model.update(recovery(oat=70))
        self.assertFalse(receipt.accepted)
        self.assertEqual(receipt.reason, "undefined_weather_coefficient")
        self.assertEqual(model.a["heat"], [])

    def test_exponential_known_per_minute_decay_at_regular_and_jittered_times(self):
        for times in ([0, 5, 10, 15], [0, 1.5, 4, 7.25, 12.5]):
            for mode in ("heat", "cool"):
                with self.subTest(times=times, mode=mode):
                    sign = -1 if mode == "heat" else 1
                    trace = [(minute, 70 + sign * 5 * 0.9 ** minute) for minute in times]
                    model = PNNLModel4()
                    receipt = model.update(recovery(mode, t=None, complete=False, traj=trace))
                    self.assertTrue(receipt.accepted)
                    self.assertAlmostEqual(receipt.parameters["c_per_minute"], 0.9, places=8)
                    self.assertAlmostEqual(model.predict(mode, trace[0][1], 70, 30),
                                           math.log(1 / 5) / math.log(0.9), places=6)

    def test_exponential_regular_cadence_conversion_is_not_double_clipped(self):
        # Source per-sample bound=.999; a five-minute interval means .999**.2
        # per minute, which is >.999. Re-clipping it per minute would change time.
        model = PNNLModel4()
        receipt = model.update(recovery(t=None, complete=False, traj=[(0, 65), (5, 64)]))
        self.assertTrue(receipt.accepted)
        self.assertAlmostEqual(receipt.parameters["c_per_minute"], 0.999 ** 0.2)

    def test_exponential_does_not_carry_last_error_into_next_event(self):
        model = PNNLModel4()
        for start_gap in (5, 20):
            trace = [(t, 70 - start_gap * 0.8 ** t) for t in (0, 1, 2)]
            receipt = model.update(recovery(start=trace[0][1], t=None, complete=False, traj=trace))
            self.assertAlmostEqual(receipt.parameters["c_per_minute"], 0.8)

    def test_median_uses_distinct_post_weekend_banks(self):
        model = PNNLMedian()
        weekday = model.update(recovery())
        self.assertTrue(weekday.accepted)
        self.assertEqual(weekday.details["bank"], "weekday")
        before = model.predict("heat", 65, 70, 30)
        self.assertEqual(before, 40)
        self.assertEqual(model.predict("heat", 65, 70, 30, True), before)
        receipt = model.update(recovery(duration=80, post_weekend=True))
        self.assertTrue(receipt.accepted)
        self.assertTrue(model.weekend_trained)
        self.assertEqual(model.predict("heat", 65, 70, 30), before)
        self.assertEqual(model.predict("heat", 65, 70, 30, True), 80)
        self.assertEqual(model.banks[False][0].window, 8)
        self.assertEqual(model.banks[True][0].window, 4)

    def test_rolling_window_is_chronological_not_sorted_by_coefficient(self):
        model = PNNLModel2(window=2)
        for duration in (40, 80, 20):
            model.update(recovery(duration=duration))
        self.assertEqual(model.rate["heat"], [0.05, 0.2])
        self.assertEqual(pnnl_ema(model.rate["heat"]), 0.2)


class ComparisonAndReceiptTests(unittest.TestCase):
    def test_linear_ema_updates_rate_not_minutes_per_degree(self):
        model = LinearRateEMA()
        receipt = model.update(recovery(duration=20))
        self.assertAlmostEqual(receipt.parameters["rate"], 0.12)
        self.assertAlmostEqual(model.predict("heat", 65, 70, 30), 4 / 0.12)

    def test_native_weight_matches_two_old_plus_one_new(self):
        model = NativeMinutesPerDegree(prior=10)
        receipt = model.update(recovery(duration=20))
        self.assertAlmostEqual(receipt.parameters["minutes_per_degree"], (2 * 10 + 20 / 4) / 3)
        self.assertAlmostEqual(model.predict("heat", 65, 70, 30), 4 * (25 / 3))
        self.assertEqual(model.minutes_per_degree["cool"], 10)

    def test_native_accepts_tiny_correct_direction_partial_below_deviation(self):
        for mode, start, end in (("heat", 65, 65.001), ("cool", 75, 74.999)):
            with self.subTest(mode=mode):
                model = NativeMinutesPerDegree(prior=10, allowable_deviation=2)
                event = recovery(mode, t=None, complete=False, start=start,
                                 traj=[(0, start), (5, end)])
                receipt = model.update(event)
                self.assertTrue(receipt.accepted)
                observed = 5 / abs(end - start)
                self.assertAlmostEqual(receipt.parameters["minutes_per_degree"], (20 + observed) / 3)
                self.assertFalse(receipt.details["complete"])

    def test_native_has_no_minimum_sample_count_for_observed_positive_response(self):
        model = NativeMinutesPerDegree(prior=10)
        receipt = model.update(recovery(t=None, complete=False, traj=[(1, 65.001)]))
        self.assertTrue(receipt.accepted)

    def test_native_reports_wrong_direction_without_mutating_state(self):
        model = NativeMinutesPerDegree(prior=10)
        receipt = model.update(recovery(t=None, complete=False, traj=[(0, 65), (5, 64)]))
        self.assertFalse(receipt.accepted)
        self.assertEqual(receipt.reason, "no_correct_direction_response")
        self.assertEqual(model.minutes_per_degree["heat"], 10)

    def test_censored_duration_without_measured_response_is_not_a_training_label(self):
        for cls in (PNNLModel1, PNNLModel2, PNNLModel3, LinearRateEMA):
            with self.subTest(model=cls.name):
                model = cls()
                receipt = model.update(recovery(t=None, complete=False, traj=[]))
                self.assertFalse(receipt.accepted)
                self.assertEqual(receipt.reason, "no_measured_response")
                self.assertEqual(json.loads(json.dumps(receipt.as_dict()))["accepted"], False)

    def test_bad_chronology_is_not_repaired_or_learned(self):
        for cls in (PNNLModel1, PNNLModel2, PNNLModel3, PNNLModel4,
                    LinearRateEMA, NativeMinutesPerDegree, G36RecoveryLearner):
            with self.subTest(model=cls.name):
                model = cls()
                receipt = model.update(recovery(traj=[(0, 65), (5, 66), (4, 67)]))
                self.assertFalse(receipt.accepted)
                self.assertEqual(receipt.reason, "invalid_trajectory")

    def test_zero_duration_is_rejected_as_mathematically_undefined(self):
        model = PNNLModel2()
        receipt = model.update(recovery(t=0, traj=[(0, 65)]))
        self.assertFalse(receipt.accepted)
        self.assertEqual(receipt.reason, "invalid_observation_duration")

    def test_legacy_comparison_uses_actual_elapsed_intervals(self):
        model = G36RecoveryLearner()
        # Both samples have .2 F/min; EMA .1 -> .15 -> .175.
        model.update(recovery(traj=[(0, 65), (2, 65.4), (7, 66.4)]))
        self.assertAlmostEqual(model.rate["heat"], 0.175)

    def test_every_estimator_has_same_endpoint(self):
        for model in default_models(allowable_deviation=1).values():
            for mode, temp in (("heat", 69), ("cool", 71)):
                with self.subTest(model=model.name, mode=mode):
                    self.assertEqual(model.predict(mode, temp, 70, 30), 0)

    def test_models_import_without_site_packages(self):
        root = Path(__file__).resolve().parents[1]
        code = "from hvac_optimal.models import default_models; print(len(default_models()))"
        result = subprocess.run([sys.executable, "-S", "-c", code], cwd=root, text=True,
                                capture_output=True, check=True)
        self.assertEqual(result.stdout.strip(), "8")

    def test_trajectory_iterables_are_materialized_before_validation_and_fit(self):
        for model in default_models().values():
            with self.subTest(model=model.name):
                event = recovery()
                event["traj"] = (point for point in event["traj"])
                receipt = model.update(event)
                self.assertTrue(receipt.accepted, receipt.as_dict())

    def test_models_without_weather_term_do_not_require_outdoor_sensor(self):
        for cls in (PNNLModel1, PNNLModel4, LinearRateEMA, NativeMinutesPerDegree, G36RecoveryLearner):
            with self.subTest(model=cls.name):
                model = cls()
                model.update(recovery())
                self.assertIsNotNone(model.predict("heat", 65, 70, None))
        for cls in (PNNLModel2, PNNLModel3):
            with self.subTest(model=cls.name):
                model = cls()
                model.update(recovery())
                self.assertIsNone(model.predict("heat", 65, 70, None))
                self.assertEqual(model.last_prediction_reason, "nonfinite_outdoor_temperature")

    def test_rate_models_fit_tiny_positive_partial_observations_without_labeling_full_duration(self):
        for cls in (PNNLModel2, LinearRateEMA):
            for mode, start, end in (("heat", 65, 65.001), ("cool", 75, 74.999)):
                with self.subTest(model=cls.name, mode=mode):
                    model = cls()
                    event = recovery(mode, start=start, t=None, complete=False,
                                     traj=[(0, start), (5, end)])
                    receipt = model.update(event)
                    self.assertTrue(receipt.accepted, receipt.as_dict())
                    self.assertEqual(receipt.reason, "fitted_partial_rate")
                    self.assertEqual(receipt.details["fit_quantity"], "observed_rate")
                    self.assertFalse(receipt.details["target_duration_inferred"])
                    self.assertFalse(receipt.details["complete"])
                    expected = abs(end - start) / 5
                    observed = receipt.parameters.get("observed_rate", receipt.parameters["rate"])
                    self.assertAlmostEqual(observed, expected)
                    self.assertEqual(receipt.details["observed_duration_minutes"], 5)

    def test_rate_fit_uses_actual_response_not_target_time_or_target_gap(self):
        event = recovery(t=10, complete=True, traj=[(0, 65), (20, 67)])
        model = PNNLModel2()
        receipt = model.update(event)
        self.assertTrue(receipt.accepted)
        self.assertEqual(receipt.parameters["rate"], 2 / 20)
        self.assertEqual(receipt.details["observed_duration_minutes"], 20)
        self.assertEqual(receipt.details["observed_change_f"], 2)

    def test_rate_fit_does_not_require_a_tolerance_sized_initial_gap(self):
        for cls in (PNNLModel2, LinearRateEMA):
            with self.subTest(model=cls.name):
                model = cls(allowable_deviation=1)
                event = recovery(start=69.5, t=None, complete=False,
                                 traj=[(0, 69.5), (1, 69.501)])
                self.assertTrue(model.update(event).accepted)
                self.assertEqual(model.predict("heat", 69.5, 70, 30), 0)

    def test_partial_curve_fits_keep_source_initial_gap_structure(self):
        event = recovery(t=None, complete=False, traj=[(0, 65), (5, 66), (10, 67)])
        johnson = PNNLModel1()
        receipt = johnson.update(event)
        self.assertTrue(receipt.accepted)
        # Source structure uses initial required gap=4, not observed change=2.
        self.assertEqual(receipt.parameters, {"a": 5 / 16, "b": 5})
        self.assertEqual(receipt.reason, "fitted_partial_curve")
        self.assertFalse(receipt.details["target_duration_inferred"])
        self.assertTrue(receipt.details["initial_gap_denominator"])
        siemens = PNNLModel3()
        heat = siemens.update(event)
        self.assertTrue(heat.accepted)
        self.assertEqual(heat.parameters, {"a": 5.0, "b": 0.0, "adjust_time": 0.0})
        self.assertEqual(heat.reason, "fitted_partial_curve")

    def test_siemens_cooling_can_fit_subdegree_partial_but_heating_requires_first_degree(self):
        model = PNNLModel3()
        cooling = recovery("cool", t=None, complete=False, traj=[(0, 75), (5, 74.999)])
        receipt = model.update(cooling)
        self.assertTrue(receipt.accepted)
        self.assertIsNone(receipt.details["first_degree"])
        self.assertAlmostEqual(receipt.parameters["a"], 5 / (75 - 74.999))
        self.assertEqual(receipt.parameters["b"], 0)
        heating = recovery(t=None, complete=False, traj=[(0, 65), (5, 65.001)])
        for cls in (PNNLModel1, PNNLModel3):
            with self.subTest(model=cls.name):
                rejected = cls().update(heating)
                self.assertFalse(rejected.accepted)
                self.assertEqual(rejected.reason, "first_degree_not_observed")

    def test_retry_does_not_fit_an_accepted_scalar_observation_twice(self):
        for cls in (PNNLModel2, LinearRateEMA, NativeMinutesPerDegree, PNNLModel4, G36RecoveryLearner):
            with self.subTest(model=cls.name):
                model = cls()
                partial = recovery(t=None, complete=False, traj=[(0, 65), (5, 65.001)])
                first = model.update(partial)
                self.assertTrue(first.accepted)
                state = copy.deepcopy({key: value for key, value in model.__dict__.items()
                                       if key != "last_training_receipt"})
                retried = model.retry_rejected(recovery(), first.as_dict())
                self.assertFalse(retried.accepted)
                self.assertEqual(retried.reason, "already_fitted_for_episode")
                self.assertTrue(retried.details["episode_fit_accepted"])
                self.assertFalse(retried.details["fit_performed"])
                again = model.retry_rejected(recovery(), retried)
                self.assertFalse(again.accepted)
                self.assertEqual({key: value for key, value in model.__dict__.items()
                                  if key != "last_training_receipt"}, state)

    def test_rejected_curve_can_fit_when_same_episode_later_supplies_first_degree(self):
        model = PNNLModel1()
        partial = recovery(t=None, complete=False, traj=[(0, 65), (5, 65.001)])
        rejected = model.update(partial)
        self.assertFalse(rejected.accepted)
        receipt = model.retry_rejected(recovery(), rejected)
        self.assertTrue(receipt.accepted)
        self.assertEqual(receipt.parameters, {"a": 35 / 16, "b": 5})
        self.assertTrue(receipt.details["episode_fit_accepted"])
        model.retry_rejected(recovery(), receipt)
        self.assertEqual(len(model.a["heat"]), 1)

    def test_median_retry_is_constituent_aware_and_keeps_accepted_partial_fits(self):
        model = PNNLMedian()
        partial = recovery(t=None, complete=False, traj=[(0, 65), (5, 65.001)])
        first = model.update(partial)
        self.assertTrue(first.accepted)  # Carrier and Sbs, but not Johnson/heating Siemens.
        self.assertEqual([child["accepted"] for child in first.details["children"]], [False, True, False, True])
        carrier_rate = list(model.banks[False][1].rate["heat"])
        sbs_decay = list(model.banks[False][3].c["heat"])
        retried = model.retry_rejected(recovery(), first)
        self.assertTrue(retried.accepted)
        self.assertEqual([child["accepted"] for child in retried.details["children"]], [True, False, True, False])
        self.assertEqual(model.banks[False][1].rate["heat"], carrier_rate)
        self.assertEqual(model.banks[False][3].c["heat"], sbs_decay)
        self.assertEqual(len(model.banks[False][0].a["heat"]), 1)
        self.assertEqual(len(model.banks[False][2].a["heat"]), 1)
        again = model.retry_rejected(recovery(), retried)
        self.assertFalse(again.accepted)
        self.assertTrue(again.details["episode_fit_accepted"])
        self.assertEqual(len(model.banks[False][0].a["heat"]), 1)
        self.assertEqual(len(model.banks[False][1].rate["heat"]), 1)
        self.assertEqual(len(model.banks[False][2].a["heat"]), 1)
        self.assertEqual(len(model.banks[False][3].c["heat"]), 1)

    def test_retry_requires_original_model_and_composite_bank_receipts(self):
        other = PNNLModel2().update(recovery())
        with self.assertRaisesRegex(ValueError, "same model"):
            PNNLModel1().retry_rejected(recovery(), other)
        median = PNNLMedian()
        receipt = median.update(recovery())
        with self.assertRaisesRegex(ValueError, "same episode's model bank"):
            median.retry_rejected(recovery(post_weekend=True), receipt)


if __name__ == "__main__":
    unittest.main()
