"""Fixed AHU-local selection, weighting and explicit input-failure evidence."""
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import unittest

from hvac_optimal.sampling import MissingSelectedZoneError, ZoneInputError, ZoneSampler


class ZoneSamplerTests(unittest.TestCase):
    def test_thirty_percent_ceil_with_at_least_one(self):
        for count, expected in ((1, 1), (2, 1), (5, 2), (6, 2), (10, 3), (11, 4), (100, 30)):
            with self.subTest(count=count):
                sampler = ZoneSampler("AHU-1", [f"zone-{i}" for i in range(count)])
                self.assertEqual(len(sampler.selected_zone_ids), expected)
                receipt = sampler.selection_receipt()
                self.assertEqual(receipt["actual_fraction"], expected / count)
                self.assertEqual(receipt["requested_fraction"], 0.3)

    def test_selection_is_independent_of_mapping_order(self):
        zones = [f"zone-{i:02d}" for i in range(35)]
        first = ZoneSampler("AHU-1", zones, seed="run-A")
        shuffled = zones[::2] + zones[1::2]
        second = ZoneSampler("AHU-1", reversed(shuffled), seed="run-A")
        self.assertEqual(first.selected_zone_ids, second.selected_zone_ids)
        self.assertEqual(first.selection_receipt(), second.selection_receipt())

    def test_selection_is_stable_across_process_and_hash_seed(self):
        root = Path(__file__).resolve().parents[1]
        code = ("import json; from hvac_optimal.sampling import ZoneSampler; "
                "zones={f'z{i}' for i in range(50)}; "
                "types={z:('exterior' if int(z[1:])%2 else 'interior') for z in zones}; "
                "print(json.dumps(ZoneSampler('AHU-1', zones, seed=123, zone_types=types).selected_zone_ids))")
        outputs = []
        for hash_seed in ("7", "593"):
            environment = dict(os.environ, PYTHONHASHSEED=hash_seed)
            result = subprocess.run([sys.executable, "-S", "-c", code], cwd=root,
                                    env=environment, capture_output=True, text=True, check=True)
            outputs.append(json.loads(result.stdout))
        self.assertEqual(outputs[0], outputs[1])

    def test_each_ahu_uses_only_its_explicit_mapping(self):
        # Deliberately misleading names: the membership lists are authoritative.
        first = ZoneSampler("AHU-A", ["AHU-B-room1", "odd:second"], fraction=1)
        second = ZoneSampler("AHU-B", ["AHU-A-room9", "another-room"], fraction=1)
        temperatures = {"AHU-B-room1": 60, "odd:second": 70,
                        "AHU-A-room9": 80, "another-room": 90, "unmapped": -10000}
        self.assertEqual(first.read(temperatures), 65)
        self.assertEqual(second.read(temperatures), 85)
        self.assertTrue(set(first.selected_zone_ids).isdisjoint(second.selected_zone_ids))

    def test_weighted_mean_and_equal_weight_default(self):
        temperatures = {"a": 60, "b": 80, "outside": -999}
        equal = ZoneSampler("AHU", ["a", "b"], selected_zone_ids=["a", "b"])
        weighted = ZoneSampler("AHU", ["a", "b"], weights={"a": 1, "b": 3},
                               selected_zone_ids=["a", "b"])
        self.assertEqual(equal.read(temperatures), 70)
        value, receipt = weighted.read(temperatures, with_receipt=True)
        self.assertEqual(value, 75)
        self.assertEqual(receipt["weights"], {"a": 1.0, "b": 3.0})
        self.assertEqual(receipt["normalized_weights"], {"a": 0.25, "b": 0.75})

    def test_missing_configured_weights_default_to_one_without_changing_selection(self):
        sampler = ZoneSampler("AHU", ["a", "b", "c"], weights={"a": 3},
                              selected_zone_ids=["a", "b"])
        self.assertEqual(sampler.read({"a": 60, "b": 80}), 65)
        self.assertEqual(sampler.weights, {"a": 3.0, "b": 1.0})

    def test_weights_do_not_determine_which_zones_are_sampled(self):
        zones = [f"z{i}" for i in range(30)]
        equal = ZoneSampler("AHU", zones, seed=55)
        weighted = ZoneSampler("AHU", zones, seed=55, weights={zone: i + 1 for i, zone in enumerate(zones)})
        self.assertEqual(equal.selected_zone_ids, weighted.selected_zone_ids)

    def test_explicit_selection_is_exact_and_actual_fraction_is_visible(self):
        sampler = ZoneSampler("AHU", ["a", "b", "c", "d"], selected_zone_ids=["d", "b"])
        self.assertEqual(sampler.selected_zone_ids, ("b", "d"))
        receipt = sampler.selection_receipt()
        self.assertEqual(receipt["selection_method"], "explicit_selection")
        self.assertEqual(receipt["requested_fraction"], 0.3)
        self.assertEqual(receipt["actual_fraction"], 0.5)
        restored = ZoneSampler(receipt["ahu_id"], receipt["mapped_zone_ids"],
                               selected_zone_ids=receipt["selected_zone_ids"], weights=receipt["weights"])
        self.assertEqual(restored.selected_zone_ids, sampler.selected_zone_ids)

    def test_foreign_selected_zone_or_weight_is_a_configuration_error(self):
        for options in ({"selected_zone_ids": ["foreign"]}, {"weights": {"foreign": 2}}):
            with self.subTest(options=options):
                with self.assertRaisesRegex(ValueError, "outside its explicit mapping"):
                    ZoneSampler("AHU", ["mapped"], **options)

    def test_missing_selected_input_never_resamples(self):
        sampler = ZoneSampler("AHU", ["a", "b", "c"], selected_zone_ids=["a", "b"])
        before = sampler.selection_receipt()
        with self.assertRaises(MissingSelectedZoneError) as caught:
            sampler.read({"a": 60, "c": 80})
        self.assertEqual(caught.exception.ahu_id, "AHU")
        self.assertEqual(caught.exception.missing_zone_ids, ("b",))
        self.assertEqual(sampler.selection_receipt(), before)
        self.assertEqual(sampler.read({"a": 60, "b": 80, "c": -999}), 70)

    def test_selected_nonfinite_values_propagate_without_sensor_filter(self):
        sampler = ZoneSampler("AHU", ["a", "b"], fraction=1)
        selected_before = sampler.selected_zone_ids
        self.assertTrue(math.isnan(sampler.read({"a": float("nan"), "b": 70})))
        self.assertEqual(sampler.read({"a": float("inf"), "b": 70}), float("inf"))
        self.assertEqual(sampler.selected_zone_ids, selected_before)

    def test_unselected_inputs_are_not_required_or_inspected(self):
        sampler = ZoneSampler("AHU", ["a", "b", "c"], selected_zone_ids=["a"])
        self.assertEqual(sampler.read({"a": 70, "b": "bad", "c": float("nan")}), 70)

    def test_nonnumeric_selected_temperature_is_explicit_input_error(self):
        sampler = ZoneSampler("AHU", ["a"])
        with self.assertRaisesRegex(ZoneInputError, "selected zone 'a'.*nonnumeric"):
            sampler.read({"a": None})
        self.assertEqual(sampler.selected_zone_ids, ("a",))

    def test_configuration_copies_weights_and_receipt_cannot_mutate_it(self):
        weights = {"a": 1, "b": 3}
        sampler = ZoneSampler("AHU", ["a", "b"], fraction=1, weights=weights)
        weights["a"] = 500
        receipt = sampler.selection_receipt()
        receipt["weights"]["a"] = 600
        receipt["selected_zone_ids"].clear()
        self.assertEqual(sampler.read({"a": 60, "b": 80}), 75)
        with self.assertRaises(TypeError):
            sampler.weights["a"] = 700

    def test_invalid_configuration_is_rejected(self):
        for zones in ([], ["a", "a"], [""], "single-string"):
            with self.subTest(zones=zones):
                with self.assertRaises(ValueError):
                    ZoneSampler("AHU", zones)
        for fraction in (0, -0.2, 1.1, float("nan"), float("inf")):
            with self.subTest(fraction=fraction):
                with self.assertRaises(ValueError):
                    ZoneSampler("AHU", ["a"], fraction=fraction)
        for weight in (0, -1, float("nan"), float("inf"), "bad"):
            with self.subTest(weight=weight):
                with self.assertRaises(ValueError):
                    ZoneSampler("AHU", ["a"], weights={"a": weight})

    def test_temperature_units_are_not_converted(self):
        sampler = ZoneSampler("AHU", ["a", "b"], fraction=1)
        self.assertEqual(sampler.read({"a": 20, "b": 24}), 22)
        self.assertEqual(sampler.read({"a": 68, "b": 75.2}), 71.6)

    def test_balanced_counts_and_odd_extra_are_deterministic(self):
        zones = [f"e{i}" for i in range(10)] + [f"i{i}" for i in range(10)]
        types = {zone: "exterior" if zone.startswith("e") else "interior" for zone in zones}
        for fraction in (0.3, 0.35):
            sampler = ZoneSampler("AHU", zones, fraction=fraction, zone_types=types, seed=12)
            counts = sampler.selection_receipt()["selected_group_counts"]
            self.assertLessEqual(abs(counts["exterior"] - counts["interior"]), 1)
            self.assertEqual(sum(counts.values()), math.ceil(fraction * len(zones)))
            self.assertEqual(counts["unknown"], 0)
            self.assertTrue(sampler.selection_receipt()["balance_achieved"])
            repeated = ZoneSampler("AHU", reversed(zones), fraction=fraction,
                                   zone_types=dict(reversed(list(types.items()))), seed=12)
            self.assertEqual(repeated.selection_receipt(), sampler.selection_receipt())

    def test_uneven_group_capacity_redistributes_unfilled_slots(self):
        zones = ["only-exterior"] + [f"i{i}" for i in range(19)]
        types = {zone: "interior" for zone in zones}
        types["only-exterior"] = "exterior"
        sampler = ZoneSampler("AHU", zones, zone_types=types)
        receipt = sampler.selection_receipt()
        self.assertEqual(receipt["selected_group_counts"], {"exterior": 1, "interior": 5, "unknown": 0})
        self.assertEqual(receipt["fallback_reason"], "known_group_capacity_redistributed")
        self.assertTrue(receipt["balance_applied"])
        self.assertFalse(receipt["balance_achieved"])

    def test_partial_classification_uses_known_balanced_pool_when_it_can_fill_sample(self):
        zones = ["e1", "e2", "i1", "i2", "u1", "u2"]
        types = {"e1": "exterior", "e2": "exterior", "i1": "interior", "i2": "interior"}
        sampler = ZoneSampler("AHU", zones, zone_types=types)
        receipt = sampler.selection_receipt()
        self.assertEqual(receipt["selected_group_counts"], {"exterior": 1, "interior": 1, "unknown": 0})
        self.assertAlmostEqual(receipt["classification_coverage"], 4 / 6)
        self.assertEqual(receipt["unknown_count"], 2)
        self.assertIsNone(receipt["fallback_reason"])

    def test_partial_classification_fills_unknown_only_after_known_pool_exhausted(self):
        zones = ["e", "i"] + [f"u{i}" for i in range(8)]
        sampler = ZoneSampler("AHU", zones, zone_types={"e": "exterior", "i": "interior"})
        receipt = sampler.selection_receipt()
        self.assertEqual(receipt["selected_group_counts"], {"exterior": 1, "interior": 1, "unknown": 1})
        self.assertEqual(receipt["unknown_count"], 8)
        self.assertEqual(receipt["fallback_reason"], "insufficient_known_zones_unknown_fill")
        self.assertFalse(receipt["balance_achieved"])

    def test_single_known_group_and_unknown_only_fallback_are_honest(self):
        zones = [f"z{i}" for i in range(10)]
        single = ZoneSampler("AHU", zones, zone_types={"z0": "exterior"})
        receipt = single.selection_receipt()
        self.assertEqual(receipt["selection_method"], "uniform_mapping_fallback")
        self.assertEqual(receipt["fallback_reason"], "only_exterior_classified")
        self.assertFalse(receipt["balance_applied"])
        self.assertFalse(receipt["balance_achieved"])
        self.assertEqual(receipt["unknown_count"], 9)
        unknown = ZoneSampler("AHU", zones)
        self.assertEqual(unknown.selection_receipt()["fallback_reason"], "no_exterior_or_interior_classification")
        self.assertEqual(unknown.selection_receipt()["selected_group_counts"]["unknown"], 3)

    def test_classification_is_explicit_not_guessed_from_zone_name(self):
        sampler = ZoneSampler("AHU", ["exterior-looking", "interior-looking"])
        self.assertEqual(sampler.selection_receipt()["unknown_count"], 2)
        with self.assertRaisesRegex(ValueError, "outside its explicit mapping"):
            ZoneSampler("AHU", ["a"], zone_types={"foreign": "interior"})
        with self.assertRaisesRegex(ValueError, "must be exterior, interior, or unknown"):
            ZoneSampler("AHU", ["a"], zone_types={"a": "probably exterior"})

    def test_explicit_selection_is_not_silently_rebalanced(self):
        zones = ["e1", "e2", "i1", "i2"]
        types = {"e1": "exterior", "e2": "exterior", "i1": "interior", "i2": "interior"}
        sampler = ZoneSampler("AHU", zones, selected_zone_ids=["e1", "e2"], zone_types=types)
        self.assertEqual(sampler.selected_zone_ids, ("e1", "e2"))
        self.assertEqual(sampler.selection_receipt()["fallback_reason"], "explicit_selection_not_rebalanced")
        self.assertFalse(sampler.selection_receipt()["balance_applied"])


if __name__ == "__main__":
    unittest.main()
