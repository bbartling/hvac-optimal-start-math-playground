"""Simulator adapter tests; importing the runner needs only the stdlib."""
from copy import deepcopy
from concurrent.futures import Future
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
import errno
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from hvac_optimal.reference import Config, Inputs
from hvac_optimal.sampling import ZoneSampler
from hvac_optimal.simulation import (
    _AHUExperiment, _atomic_json, _clean, _digest, _file_hash, ATOMIC_REPLACE_DELAYS, available_policies,
    classify_geometry, discover_scenarios, run_matrix,
)


DAY = datetime(2026, 11, 18, tzinfo=timezone.utc)


@contextmanager
def windows_read_lock(path):
    """Hold an actual Windows reader that omits FILE_SHARE_DELETE.

    Yields an idempotent release callback, useful for an actual simulator smoke
    that releases a deliberately held manifest reader on the first retry.
    """
    if os.name != "nt":
        raise RuntimeError("This sharing-mode fixture requires Windows")
    import ctypes
    from ctypes import wintypes
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.CreateFileW.argtypes = (wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                                  wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE)
    kernel.CreateFileW.restype = wintypes.HANDLE
    kernel.CloseHandle.argtypes = (wintypes.HANDLE,)
    kernel.CloseHandle.restype = wintypes.BOOL
    # GENERIC_READ; share read/write, intentionally omit share-delete; OPEN_EXISTING.
    handle = kernel.CreateFileW(str(path), 0x80000000, 0x1 | 0x2, None, 3, 0x80, None)
    if handle == ctypes.c_void_p(-1).value:
        raise ctypes.WinError(ctypes.get_last_error())

    def release():
        nonlocal handle
        if handle is not None:
            if not kernel.CloseHandle(handle):
                raise ctypes.WinError(ctypes.get_last_error())
            handle = None
    try:
        yield release
    finally:
        release()


def at(hour, minute=0):
    return DAY.replace(hour=hour, minute=minute)


def experiment(policy="native"):
    records = []
    instance = _AHUExperiment("arbitrary-AHU", ZoneSampler("arbitrary-AHU", ["arbitrary-room"], fraction=1),
                              Config(lower_comfort_limit=69.53, upper_comfort_limit=74.93), policy,
                              "UTC", lambda value: records.append(deepcopy(value)))
    return instance, records


def start_input(temp, occupied=False):
    return Inputs(space_temp=temp, outside_temp=30, start_enable=True, stop_enable=True,
                  schedule_status=occupied, next_event_value=not occupied,
                  next_event_time=at(19) if occupied else at(6))


class SimulatorAdapterTests(unittest.TestCase):
    def test_discovery_does_not_import_optional_simulator(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory) / "smart_buildings" / "training_scenarios"
            for building, weather in (("renamed-A", "weather-z"), ("renamed-B", "weather-y")):
                path = base / building / weather
                path.mkdir(parents=True)
                (path / "config.gin").write_text("# fixture", encoding="utf-8")
            before = set(sys.modules)
            rows = discover_scenarios(directory)
            self.assertEqual([row["scenario_id"] for row in rows], ["renamed-A/weather-z", "renamed-B/weather-y"])
            self.assertFalse(any(name.startswith("smart_buildings") for name in set(sys.modules) - before))

    def test_native_partial_learning_does_not_censor_later_observed_endpoint(self):
        instance, records = experiment()
        instance.tick(start_input(65), at(5, 50))
        instance.tick(start_input(67, True), at(6))
        self.assertEqual(instance.learning_events, 1)
        self.assertIsNotNone(instance.pending)
        self.assertFalse(any(row["type"] == "outcome" for row in records))
        native = next(row for row in records if row["type"] == "native_training")
        self.assertFalse(native["research_event"]["complete"])
        self.assertIsNone(native["research_event"]["t"])
        instance.tick(start_input(69, True), at(6, 10))
        outcome = next(row for row in records if row["type"] == "outcome")
        self.assertEqual(outcome["research_event"]["t"], 20)
        self.assertIsNone(instance.pending)
        self.assertEqual(instance.learning_events, 1)  # No fabricated native update.
        self.assertTrue(any(row["type"] == "deferred_research_training" for row in records))

    def test_early_endpoint_keeps_native_training_until_native_target_crossing(self):
        instance, records = experiment()
        instance.tick(start_input(65), at(5, 30))
        instance.tick(start_input(69), at(5, 40))
        outcomes = [row for row in records if row["type"] == "outcome"]
        self.assertEqual(outcomes[0]["research_event"]["t"], 10)
        self.assertEqual(instance.learning_events, 0)
        self.assertIsNotNone(instance.pending)
        instance.tick(start_input(70), at(5, 45))
        self.assertEqual(instance.learning_events, 1)
        self.assertIsNone(instance.pending)
        native = next(row for row in records if row["type"] == "native_training")
        self.assertEqual(native["research_event"]["traj"][-1], (15.0, 70))
        self.assertEqual(native["research_event"]["t"], 10)
        self.assertEqual(len([row for row in records if row["type"] == "outcome"]), 1)

    def test_independent_ahu_controllers_models_and_learning_history(self):
        left, _ = experiment()
        right, _ = experiment()
        left.tick(start_input(65), at(5, 50))
        left.tick(start_input(69.6, True), at(6))
        self.assertEqual(right.controller.state.runtime_per_degree_heating, 10)
        self.assertNotEqual(left.controller.state.runtime_per_degree_heating, 10)
        self.assertIsNot(left.models["pnnl_m1_quadratic"], right.models["pnnl_m1_quadratic"])
        self.assertEqual(right.error_histories, {})

    def test_deferred_composite_fit_retries_children_without_refitting_accepted_ones(self):
        instance, records = experiment()
        instance.tick(start_input(65), at(5, 50))
        instance.tick(start_input(65.2, True), at(6))
        ensemble = instance.models["pnnl_deployed_median_split"]
        self.assertEqual(ensemble.banks[False][0].a["heat"], [])
        instance.tick(start_input(69, True), at(6, 10))
        self.assertEqual(len(ensemble.banks[False][0].a["heat"]), 1)
        deferred = next(row for row in records if row["type"] == "deferred_research_training")
        self.assertIn("pnnl_deployed_median_split", deferred["training_receipts"])
        self.assertEqual(instance.learning_events, 1)

    def test_common_metrics_use_the_same_supported_episode_for_every_candidate(self):
        instance, _ = experiment()
        predictions = {name: 10.0 for name in instance.metrics}
        with patch.object(instance, "_predictions", return_value=predictions):
            instance.tick(start_input(65), at(5, 50))
            instance.tick(start_input(70, True), at(6))
        for metric in instance.summary()["metrics"].values():
            self.assertEqual(metric["common_assessed"], 1)
            self.assertEqual(metric["common_mae_minutes"], 0)

    def test_research_stop_returns_native_lead_and_no_prediction_call(self):
        instance, records = experiment("winner")
        self.assertEqual(instance._predict_lead("stop", Inputs(), instance.controller.state, 41), 41)
        self.assertEqual(records, [])

    def test_winner_uses_replay_selector_history_mode_weekend_and_insertion_ties(self):
        instance, records = experiment("winner")
        instance.now = at(5)
        names = list(instance.models)
        predictions = {"native_endpoint_adapter": 40, **{name: 20 for name in names}}
        for name in names:
            instance.error_histories[("heat", False)][name] = [1000] + [3] * 8
        # Other regime's spectacular errors cannot affect this selection.
        instance.error_histories[("cool", True)][names[0]] = [0]
        with patch.object(instance, "_predictions", return_value=predictions):
            lead = instance._predict_lead("start", start_input(65), instance.controller.state, 46)
        self.assertEqual(lead, 20)
        self.assertEqual(records[-1]["selected"], names[0])
        self.assertEqual(records[-1]["selection_history"]["prior_counts"][names[0]], 8)
        self.assertEqual(records[-1]["selection_history"]["prior_mae"][names[0]], 3)

    def test_winner_without_common_history_explicitly_uses_native_default(self):
        instance, records = experiment("winner")
        instance.now = at(5)
        self.assertEqual(instance._predict_lead("start", start_input(65), instance.controller.state, 46), 46)
        self.assertEqual(records[-1]["selected"], "native")
        self.assertEqual(records[-1]["selection_history"]["reason"], "no_eligible_history")

    def test_horizon_censoring_visible_and_no_fit_without_native_eligibility(self):
        instance, records = experiment()
        instance.tick(start_input(65), at(5, 50))
        instance._finish(reason="run_horizon_censored")
        outcome = next(row for row in records if row["type"] == "outcome")
        self.assertFalse(outcome["research_event"]["complete"])
        self.assertEqual(instance.training_accepted, 0)
        self.assertFalse(any(row["type"] == "native_training" for row in records))

    def test_terminal_observed_endpoint_scores_without_native_tick_or_eligibility(self):
        instance, records = experiment()
        instance.tick(start_input(65), at(5, 50))
        native_before = instance.controller.state.to_dict()
        instance.finish_horizon(69, at(6, 10))
        outcomes = [row for row in records if row["type"] == "outcome"]
        self.assertEqual(len(outcomes), 1)
        self.assertEqual(outcomes[0]["research_event"]["t"], 20)
        self.assertTrue(outcomes[0]["research_event"]["complete"])
        self.assertEqual(instance.controller.state.to_dict(), native_before)
        self.assertEqual(instance.learning_events, 0)
        self.assertEqual(instance.training_accepted, 0)
        instance.finish_horizon(70, at(6, 15))
        self.assertEqual(len([row for row in records if row["type"] == "outcome"]), 1)

    def test_terminal_late_endpoint_preserves_prior_native_update_only(self):
        instance, records = experiment()
        instance.tick(start_input(65), at(5, 50))
        instance.tick(start_input(65.2, True), at(6))
        native_before = instance.controller.state.to_dict()
        instance.finish_horizon(69, at(6, 10))
        outcome = next(row for row in records if row["type"] == "outcome")
        self.assertEqual(outcome["research_event"]["t"], 20)
        self.assertEqual(instance.controller.state.to_dict(), native_before)
        self.assertEqual(instance.learning_events, 1)
        self.assertTrue(any(row["type"] == "deferred_research_training" for row in records))

    def test_native_endpoint_shadow_explicitly_differs_from_full_target_command(self):
        instance, _ = experiment()
        instance.now = at(5)
        predictions = instance._predictions(65, 30, instance.controller.state)
        self.assertIn("native_endpoint_adapter", predictions)
        self.assertNotIn("native", predictions)
        self.assertEqual(predictions["native_endpoint_adapter"], 36)
        self.assertEqual(instance.controller._start_lead(start_input(65), 74.93, 69.53), 46)

    def test_strict_json_nonfinite_and_policy_inventory(self):
        self.assertEqual(json.loads(json.dumps(_clean({"bad": float("inf")}))), {"bad": "Infinity"})
        self.assertIn("winner", available_policies())
        self.assertIn("pnnl_m4_exponential", available_policies())

    @unittest.skipUnless(importlib.util.find_spec("numpy"), "Optional numpy is required for geometry-array test")
    def test_geometry_uses_coordinates_not_point_names(self):
        import numpy as np
        walls = np.zeros((8, 8))
        walls[0, :] = -2
        # Names deliberately contradict the actual geometry.
        labels, evidence = classify_geometry({"interior-looking-name": [(1, 3)], "exterior-looking-name": [(5, 3)]}, walls)
        self.assertEqual(labels["interior-looking-name"], "exterior")
        self.assertEqual(labels["exterior-looking-name"], "interior")
        self.assertIn("coordinates", evidence["method"])


class AtomicPublicationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.directory = Path(self.temporary.name)
        self.destination = self.directory / "manifest.json"
        self.original = '{"old": true}\n'
        self.destination.write_text(self.original, encoding="utf-8")

    def tearDown(self):
        self.temporary.cleanup()

    def assert_no_owned_temporary(self):
        self.assertEqual(list(self.directory.glob("manifest.json.*.tmp")), [])

    def test_transient_permission_error_retries_then_publishes(self):
        real_replace = os.replace
        attempts = 0
        def replace(source, target):
            nonlocal attempts
            attempts += 1
            if attempts <= 2:
                raise PermissionError("temporary reader denies delete sharing")
            return real_replace(source, target)
        with patch("hvac_optimal.simulation.os.replace", side_effect=replace) as replacement, patch("hvac_optimal.simulation.time.sleep") as sleep:
            _atomic_json(self.destination, {"complete": 1})
        self.assertEqual(replacement.call_count, 3)
        self.assertEqual([call.args[0] for call in sleep.call_args_list], list(ATOMIC_REPLACE_DELAYS[:2]))
        self.assertEqual(json.loads(self.destination.read_text()), {"complete": 1})
        self.assert_no_owned_temporary()

    def test_permanent_permission_error_is_bounded_and_cleans_temporary(self):
        error = PermissionError("permanent destination denial")
        with patch("hvac_optimal.simulation.os.replace", side_effect=error) as replacement, patch("hvac_optimal.simulation.time.sleep") as sleep:
            with self.assertRaises(PermissionError) as caught:
                _atomic_json(self.destination, {"complete": 1})
        self.assertIs(caught.exception, error)
        self.assertEqual(replacement.call_count, len(ATOMIC_REPLACE_DELAYS) + 1)
        self.assertEqual([call.args[0] for call in sleep.call_args_list], list(ATOMIC_REPLACE_DELAYS))
        self.assertEqual(self.destination.read_text(), self.original)
        self.assert_no_owned_temporary()

    def test_other_oserror_is_not_retried_and_keeps_original(self):
        error = OSError(errno.ENOSPC, "fixture disk full")
        with patch("hvac_optimal.simulation.os.replace", side_effect=error) as replacement, patch("hvac_optimal.simulation.time.sleep") as sleep:
            with self.assertRaises(OSError) as caught:
                _atomic_json(self.destination, {"complete": 1})
        self.assertIs(caught.exception, error)
        self.assertEqual(replacement.call_count, 1)
        sleep.assert_not_called()
        self.assertEqual(self.destination.read_text(), self.original)
        self.assert_no_owned_temporary()

    def test_serialization_error_cleans_partial_temporary_without_replace(self):
        with patch("hvac_optimal.simulation.os.replace") as replacement, patch("hvac_optimal.simulation.time.sleep") as sleep:
            with self.assertRaises(TypeError):
                _atomic_json(self.destination, {"not_json": object()})
        replacement.assert_not_called()
        sleep.assert_not_called()
        self.assertEqual(self.destination.read_text(), self.original)
        self.assert_no_owned_temporary()

    @unittest.skipUnless(os.name == "nt", "Windows delete-sharing fixture requires CreateFileW")
    def test_actual_windows_reader_without_delete_sharing_releases_on_retry(self):
        with windows_read_lock(self.destination) as release:
            # The first REAL os.replace must fail while the reader is open.
            # Release that actual OS handle at the retry wait, then use real
            # os.replace again. No filesystem error is mocked in this test.
            with patch("hvac_optimal.simulation.time.sleep", side_effect=lambda _delay: release()) as sleep:
                _atomic_json(self.destination, {"complete": 1})
            self.assertEqual(sleep.call_count, 1)
        self.assertEqual(json.loads(self.destination.read_text()), {"complete": 1})
        self.assert_no_owned_temporary()


class MatrixReceiptTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary.name)
        self.kit = self.base / "kit"
        scenario = self.kit / "smart_buildings" / "training_scenarios" / "renamed" / "weather"
        scenario.mkdir(parents=True)
        (scenario / "config.gin").write_text("# fixture", encoding="utf-8")
        self.out = self.base / "output"

    def tearDown(self):
        self.temporary.cleanup()

    def job(self, job):
        history = Path(job["out"]) / (job["job_id"] + ".jsonl.gz")
        history.write_bytes(b"fixture artifact")
        result = {**job, "status": "complete", "steps_completed": job["steps"],
                  "history_path": str(history), "history_sha256": _file_hash(history)}
        directory = Path(job["out"]) / "jobs"
        directory.mkdir(exist_ok=True)
        (directory / (job["job_id"] + ".json")).write_text(json.dumps(result), encoding="utf-8")
        return result

    def test_resume_requires_exact_steps_and_signature(self):
        with patch("hvac_optimal.simulation._run_job", side_effect=self.job) as worker, patch("hvac_optimal.simulation._tree_hash", return_value="fixture-sha"):
            first = run_matrix(self.kit, self.out, steps=12, workers=1)
            again = run_matrix(self.kit, self.out, steps=12, workers=1)
            self.assertEqual((first["complete"], again["complete"], worker.call_count), (1, 1, 1))
            with self.assertRaises(FileExistsError):
                run_matrix(self.kit, self.out, steps=8640, workers=1)
            with self.assertRaises(FileExistsError):
                run_matrix(self.kit, self.out, steps=12, workers=1, sample_fraction=.5)
            with self.assertRaises(FileExistsError):
                run_matrix(self.kit, self.out, steps=12, workers=1, resume=False)

    def test_dirty_directory_is_not_overwritten(self):
        self.out.mkdir()
        marker = self.out / "unrecognized.txt"
        marker.write_text("keep", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            run_matrix(self.kit, self.out, steps=12, workers=1)
        self.assertEqual(marker.read_text(), "keep")

    def test_missing_or_changed_history_requires_new_attempt(self):
        with patch("hvac_optimal.simulation._run_job", side_effect=self.job) as worker, patch("hvac_optimal.simulation._tree_hash", return_value="fixture-sha"):
            first = run_matrix(self.kit, self.out, steps=12, workers=1)
            history = Path(first["results"][0]["history_path"])
            history.write_bytes(b"tampered")
            run_matrix(self.kit, self.out, steps=12, workers=1)
            self.assertEqual(worker.call_count, 2)

    def test_failure_count_and_atomic_status_are_explicit(self):
        with patch("hvac_optimal.simulation._run_job", side_effect=lambda job: {**job, "status": "failed", "steps_completed": 0, "error": "fixture failure"}):
            result = run_matrix(self.kit, self.out, steps=12, workers=1)
        self.assertEqual(result["failed"], 1)
        self.assertEqual(result["status"], "failed")
        self.assertEqual(json.loads((self.out / "manifest.json").read_text())["pending"], 0)

    def test_publication_error_is_not_a_fake_worker_failure_and_resume_recovers(self):
        publication_error = PermissionError("fixture permanent manifest publication error")
        real_atomic = _atomic_json
        publications = []
        def publish(path, value):
            publications.append(deepcopy(value))
            if len(publications) == 2:
                raise publication_error
            return real_atomic(path, value)
        def submit(_function, job):
            future = Future()
            future.set_result(self.job(job))  # Complete durable worker result.
            return future
        with patch("hvac_optimal.simulation.ProcessPoolExecutor") as executor, patch("hvac_optimal.simulation._tree_hash", return_value="fixture-sha"):
            executor.return_value.__enter__.return_value.submit.side_effect = submit
            with patch("hvac_optimal.simulation._atomic_json", side_effect=publish):
                with self.assertRaises(PermissionError) as caught:
                    run_matrix(self.kit, self.out, steps=12, workers=2)
            self.assertIs(caught.exception, publication_error)
            self.assertEqual(len(publications), 2)  # No fake failed publication.
            self.assertEqual(len(publications[-1]["results"]), 1)
            self.assertEqual(publications[-1]["results"][0]["status"], "complete")
            self.assertEqual(publications[-1]["failed"], 0)
            with patch("hvac_optimal.simulation._run_job", side_effect=AssertionError("valid receipt must not rerun")) as worker:
                recovered = run_matrix(self.kit, self.out, steps=12, workers=1)
            worker.assert_not_called()
        self.assertEqual((recovered["complete"], recovered["failed"], recovered["pending"]), (1, 0, 0))
        self.assertEqual(len(recovered["results"]), 1)

    def test_exceptional_future_records_exactly_one_worker_failure(self):
        def submit(_function, _job):
            future = Future()
            future.set_exception(RuntimeError("fixture worker exploded"))
            return future
        with patch("hvac_optimal.simulation.ProcessPoolExecutor") as executor:
            executor.return_value.__enter__.return_value.submit.side_effect = submit
            result = run_matrix(self.kit, self.out, steps=12, workers=2)
        self.assertEqual((result["complete"], result["failed"], result["pending"]), (0, 1, 0))
        self.assertEqual(len(result["results"]), 1)
        self.assertIn("fixture worker exploded", result["results"][0]["error"])


if __name__ == "__main__":
    unittest.main()
