"""Source-traceable native start/stop tests; no third-party dependencies."""

from dataclasses import asdict, replace
from datetime import datetime, time, timedelta, timezone
import json
import math
from pathlib import Path
import random
import sys
import unittest

from hvac_optimal.reference import (
    Command, Config, EPOCH, Inputs, OptimizedStartStop, RATE_NAMES,
    ResearchOptimizedStartStop, State, TimeAdapter,
    START_CALCULATION, START_IN_PROCESS, STOP_CALCULATION, STOP_IN_PROCESS,
    float32, ieee_divide, int32, java_int,
)

sys.path.insert(0, str(Path(__file__).resolve().parent))
from java_oracle.runner import JavaUnavailable, OracleSourceUnavailable, run_oracle


DAY = datetime(2026, 11, 18, tzinfo=timezone.utc)


def at(hour, minute=0, second=0, microsecond=0):
    return DAY.replace(hour=hour, minute=minute, second=second, microsecond=microsecond)


def starting(**changes):
    values = dict(space_temp=60.0, outside_temp=30.0, start_enable=True,
                  next_event_time=at(8), next_event_value=True)
    values.update(changes)
    return Inputs(**values)


def stopping(**changes):
    values = dict(space_temp=72.0, outside_temp=30.0, stop_enable=True,
                  schedule_status=True, next_event_time=at(18), next_event_value=False)
    values.update(changes)
    return Inputs(**values)


class NativeReferenceTests(unittest.TestCase):
    def test_defaults_and_user_parameters_are_separate(self):
        controller = OptimizedStartStop()
        self.assertEqual([getattr(controller.state, key) for key in RATE_NAMES], [10.0] * 4)
        self.assertEqual(list(controller.user_parameters.values()), [0.0] * 4)
        self.assertEqual(controller.config.earliest_start_time, time(0, 0, 10))
        self.assertEqual(controller.config.earliest_stop_time, time(16))

    def test_start_lead_truncates_then_adds_one_and_ignores_heat_cool_mode(self):
        for temperature, mode, expected in ((60, True, 81), (80.19, False, 32),
                                             (68, True, 0), (77, False, 0)):
            with self.subTest(temperature=temperature, mode=mode):
                result = OptimizedStartStop().tick(starting(space_temp=temperature, heat_cool_mode=mode), now=at(1))
                self.assertEqual(result.state.lead_time, expected)
                self.assertEqual(result.state.program_mode, START_CALCULATION)

    def test_stop_lead_signs_and_no_plus_one(self):
        for temperature, cooling, expected in ((72.19, False, 41), (72.19, True, 48), (80, True, -30)):
            with self.subTest(temperature=temperature, cooling=cooling):
                state = OptimizedStartStop().tick(stopping(space_temp=temperature, heat_cool_mode=cooling), now=at(12)).state
                self.assertEqual(state.lead_time, expected)
                self.assertEqual(state.program_mode, STOP_CALCULATION)

    def test_stop_at_or_below_lower_retains_stale_shared_lead(self):
        for temperature in (68, 67):
            controller = OptimizedStartStop()
            controller.state.lead_time = 123
            state = controller.tick(stopping(space_temp=temperature), now=at(12)).state
            self.assertEqual(state.lead_time, 123)

    def test_strict_after_calculated_time(self):
        controller = OptimizedStartStop()
        inputs = starting()
        equal = controller.tick(inputs, now=at(6, 39))
        self.assertEqual(equal.state.program_mode, START_CALCULATION)
        after = controller.tick(inputs, now=at(6, 39, 0, 1000))
        self.assertEqual(after.state.program_mode, START_IN_PROCESS)
        self.assertEqual([event["kind"] for event in after.events], ["start"])

    def test_schedule_alternative_bypasses_earliest_stop(self):
        controller = OptimizedStartStop()
        result = controller.tick(stopping(next_event_time=at(15)), now=at(15, 0, 15))
        self.assertEqual(result.state.calculated_command_time, time(16))
        self.assertEqual(result.state.program_mode, STOP_IN_PROCESS)

    def test_both_operations_use_earliest_start_then_stop_clamp(self):
        config = Config(earliest_start_time=time(5), earliest_stop_time=time(16))
        start = OptimizedStartStop(config).tick(starting(space_temp=0), now=at(1)).state
        stop = OptimizedStartStop(config).tick(stopping(space_temp=100), now=at(1)).state
        self.assertEqual(start.calculated_command_time, time(5))
        self.assertEqual(stop.calculated_command_time, time(16))

    def test_same_day_of_year_ignores_year(self):
        state = OptimizedStartStop().tick(starting(next_event_time=at(8).replace(year=2025)), now=at(1)).state
        self.assertEqual(state.program_mode, START_CALCULATION)
        state = OptimizedStartStop().tick(starting(next_event_time=at(8) + timedelta(days=1)), now=at(1)).state
        self.assertEqual(state.program_mode, 0)

    def test_daily_start_latch_resets_only_in_first_minute_or_disabled(self):
        controller = OptimizedStartStop()
        controller.state.start_done = True
        controller.tick(starting(), now=at(0, 1))
        self.assertTrue(controller.state.start_done)
        controller.tick(starting(), now=at(0, 0, 59))
        self.assertFalse(controller.state.start_done)
        controller.state.start_done = True
        controller.tick(starting(start_enable=False), now=at(12))
        self.assertFalse(controller.state.start_done)

    def test_invalid_space_leaves_calculation_mode_and_can_trigger(self):
        controller = OptimizedStartStop()
        controller.state.program_mode = START_CALCULATION
        state = controller.tick(starting(space_temp_valid=False), now=at(8, 0, 15)).state
        self.assertEqual(state.lead_time, 0)
        self.assertEqual(state.program_mode, START_IN_PROCESS)

    def test_other_input_statuses_are_ignored(self):
        state = OptimizedStartStop().tick(starting(input_statuses={"start_enable": "fault", "outside_temp": "null"}), now=at(7)).state
        self.assertEqual(state.program_mode, START_IN_PROCESS)

    def test_output_value_null_and_opaque_status_flags(self):
        for mode, start_pair, stop_pair in ((0, (False, True), (False, True)),
                                            (2, (True, False), (False, True)),
                                            (4, (False, True), (False, False))):
            controller = OptimizedStartStop()
            controller.state.program_mode = mode
            controller.state.start_time_command = Command(status_flags=16)
            controller.state.stop_time_command = Command(status_flags=32)
            controller._output()
            self.assertEqual((controller.state.start_time_command.value, controller.state.start_time_command.status_null), start_pair)
            self.assertEqual((controller.state.stop_time_command.value, controller.state.stop_time_command.status_null), stop_pair)
            self.assertEqual(controller.state.start_time_command.status_flags, 16)
            self.assertEqual(controller.state.stop_time_command.status_flags, 32)

    def _learning(self, mode, beginning, current, cooling=False, schedule=True, **config):
        controller = OptimizedStartStop(Config(**config))
        state = controller.state
        state.program_mode = state.last_program_mode = mode
        state.space_temp_at_beginning = beginning
        state.last_start_time = state.last_stop_time = at(7)
        state.control_mode_at_beginning = cooling
        inputs = starting(space_temp=current, schedule_status=schedule) if mode == 2 else stopping(space_temp=current, schedule_status=schedule)
        result = controller.tick(inputs, now=at(7, 30))
        return controller, [event for event in result.events if event["type"] == "native_learning"]

    def test_four_independent_native_learners(self):
        cases = ((2, 80, 77, False, True, "runtime_per_degree_cooling"),
                 (2, 65, 68, True, True, "runtime_per_degree_heating"),
                 (4, 71, 68, False, False, "drifttime_per_degree_heating"),
                 (4, 74, 77, True, False, "drifttime_per_degree_cooling"))
        for mode, beginning, current, cooling, schedule, name in cases:
            with self.subTest(name=name):
                controller, events = self._learning(mode, beginning, current, cooling, schedule)
                self.assertEqual(len(events), 1)
                self.assertEqual(events[0]["parameter"], name)
                self.assertEqual(events[0]["observed_minutes_per_degree"], 10)
                self.assertTrue(events[0]["target_reached"])
                self.assertEqual([getattr(controller.state, key) for key in RATE_NAMES], [10] * 4)

    def test_arbitrarily_tiny_positive_partial_start_response_is_eligible(self):
        controller, events = self._learning(2, 60, 60 + 1e-9, schedule=True)
        self.assertEqual(len(events), 1)
        self.assertFalse(events[0]["target_reached"])
        self.assertGreater(controller.state.runtime_per_degree_heating, 1e9)

    def test_tiny_partial_stop_rounds_operands_to_zero_and_learns_infinity(self):
        controller, events = self._learning(4, 72, 72 - 1e-9, schedule=False)
        self.assertEqual(len(events), 1)
        self.assertEqual(controller.state.space_temp_change, 0)
        self.assertTrue(math.isinf(controller.state.drifttime_per_degree_heating))

    def test_no_wrong_direction_zero_or_prethreshold_learning(self):
        for mode, beginning, current, cooling, schedule in (
            (2, 60, 59, False, True), (2, 60, 60, False, True),
            (2, 60, 61, False, False), (4, 72, 73, False, False),
            (4, 72, 72, False, False), (4, 72, 71, False, True)):
            with self.subTest(mode=mode, beginning=beginning, current=current):
                _, events = self._learning(mode, beginning, current, cooling, schedule)
                self.assertEqual(events, [])

    def test_weight_is_event_alpha_one_third_in_minutes_per_degree(self):
        controller, events = self._learning(2, 60, 61.5)
        self.assertEqual(events[0]["observed_minutes_per_degree"], 20)
        self.assertEqual(controller.state.runtime_per_degree_heating, float32(40 / 3))
        controller, _ = self._learning(2, 60, 61.5, old_parameter_multiplier=0)
        self.assertEqual(controller.state.runtime_per_degree_heating, 20)
        controller, _ = self._learning(2, 60, 61.5, old_parameter_multiplier=-1)
        self.assertTrue(math.isinf(controller.state.runtime_per_degree_heating))

    def test_zero_elapsed_and_invalid_or_disabled_analysis(self):
        controller = OptimizedStartStop()
        state = controller.state
        state.program_mode = state.last_program_mode = START_IN_PROCESS
        state.space_temp_at_beginning = 60
        state.last_start_time = at(7)
        result = controller.tick(starting(space_temp=68, schedule_status=True), now=at(7, 0, 15))
        self.assertEqual(result.events[0]["observed_minutes_per_degree"], 0)
        for valid, dynamic in ((False, True), (True, False)):
            controller = OptimizedStartStop(Config(dynamic_parameter_adjust=dynamic))
            controller.state.last_program_mode = 2
            controller.state.space_temp_at_beginning = 60
            self.assertEqual(controller.tick(starting(space_temp=68, schedule_status=True, space_temp_valid=valid), now=at(8)).events, ())

    def test_analysis_uses_previous_mode_before_schedule_exit(self):
        controller, events = self._learning(2, 60, 61, schedule=True)
        self.assertEqual(len(events), 1)
        self.assertEqual(controller.state.program_mode, 0)
        self.assertFalse(controller.state.analysis_complete)
        self.assertEqual(controller.state.runtime_per_degree_heating, float32(50 / 3))

    def test_completed_analysis_not_repeated_in_process(self):
        controller = OptimizedStartStop()
        controller.state.program_mode = controller.state.last_program_mode = 2
        controller.state.space_temp_at_beginning = 60
        controller.state.last_start_time = at(7)
        first = controller.tick(starting(space_temp=68), now=at(7, 30))
        second = controller.tick(starting(space_temp=69), now=at(7, 31))
        self.assertEqual(len(first.events), 1)
        self.assertEqual(second.events, ())

    def test_start_analysis_uses_current_upper_limit_and_stop_latches_mode(self):
        controller = OptimizedStartStop(Config(upper_comfort_limit=81))
        controller.state.last_program_mode = 2
        controller.state.space_temp_at_beginning = 80
        controller.state.last_start_time = at(7)
        # Beginning 80 is no longer above the CURRENT upper limit: heating
        # classification rejects the decreasing response even at schedule.
        self.assertEqual(controller.tick(starting(space_temp=79, schedule_status=True), now=at(8)).events, ())
        controller = OptimizedStartStop()
        controller.state.program_mode = controller.state.last_program_mode = 4
        controller.state.space_temp_at_beginning = 72
        controller.state.control_mode_at_beginning = False
        controller.state.last_stop_time = at(17)
        result = controller.tick(stopping(space_temp=71, schedule_status=False, heat_cool_mode=True), now=at(18))
        self.assertEqual(result.events[0]["parameter"], "drifttime_per_degree_heating")

    def test_in_process_displayed_time_returns_to_schedule_time(self):
        controller = OptimizedStartStop()
        first = controller.tick(starting(), now=at(7))
        self.assertEqual(first.state.calculated_command_time, time(6, 39))
        second = controller.tick(starting(), now=at(7, 1))
        self.assertEqual(second.state.calculated_command_time, time(8))

    def test_user_change_does_not_reset_latches_and_has_running_steady_gates(self):
        controller = OptimizedStartStop()
        controller.state.start_done = controller.state.analysis_complete = True
        self.assertFalse(controller.user_parameter_changed("runtime_per_degree_heating_user_defined", 5, now=at(8), running=False))
        self.assertEqual(controller.state.runtime_per_degree_heating, 10)
        self.assertEqual(controller.user_parameters["runtime_per_degree_heating_user_defined"], 5)
        self.assertFalse(controller.user_parameter_changed("runtimePerDegreeHeatingUserDefined", 6, now=at(8), steady_state=False))
        self.assertTrue(controller.user_parameter_changed("runtimePerDegreeHeatingUserDefined", -2, now=at(8)))
        self.assertEqual(controller.state.runtime_per_degree_heating, -2)
        self.assertEqual(controller.state.parameter_reset_time, at(8))
        self.assertTrue(controller.state.start_done and controller.state.analysis_complete)

    def test_multiple_clock_reads_and_native_minute_ticket(self):
        readings = iter((at(6, 39), at(6, 39, 0, 1000), at(6, 39, 0, 2000)))
        state = OptimizedStartStop(clock=lambda: next(readings)).tick(starting()).state
        self.assertEqual(state.now, at(6, 39))
        self.assertEqual(state.last_start_time, at(6, 39, 0, 2000))
        controller = OptimizedStartStop()
        self.assertEqual(controller.next_clock_ticket(at(6, 39, 40)), at(6, 40, 15))
        self.assertEqual(controller.next_clock_ticket(at(6, 39)), at(6, 40, 15))
        self.assertEqual(controller.tick(starting(space_temp=60), now=at(1)).state.lead_time, 81)
        self.assertEqual(controller.tick(starting(space_temp=61), now=at(1, 0, 1)).state.lead_time, 71)

    def test_result_snapshot_and_strict_json_nonfinite_encoding(self):
        seen = []
        controller = OptimizedStartStop(on_event=seen.append)
        result = controller.tick(starting(), now=at(7))
        controller.state.lead_time = 3
        self.assertEqual(result.state.lead_time, 81)
        self.assertEqual(seen[0]["type"], "trigger")
        result.state.runtime_per_degree_cooling = math.inf
        self.assertIn('"Infinity"', json.dumps(result.to_dict(), allow_nan=False))

    def test_numeric_compatibility(self):
        self.assertEqual(java_int(math.nan), 0)
        self.assertEqual(java_int(math.inf), 2**31 - 1)
        self.assertEqual(java_int(-1.9), -1)
        self.assertEqual(int32(2**31), -(2**31))
        self.assertTrue(math.isnan(ieee_divide(0, 0)))
        self.assertEqual(ieee_divide(1, -0.0), -math.inf)
        self.assertEqual(float32(1e100), math.inf)
        state = OptimizedStartStop(Config(runtime_per_degree_heating=math.inf)).tick(starting(), now=at(1)).state
        self.assertEqual(state.lead_time, -(2**31))

    def test_time_adapter_signed_minutes_epoch_and_fixed_zone(self):
        adapter = TimeAdapter(timezone(timedelta(hours=-6)))
        self.assertEqual(adapter.time_of_day_millis(EPOCH), 18 * 60 * 60 * 1000)
        self.assertEqual(adapter.elapsed_minutes(at(7), at(6, 58, 30)), -1)
        self.assertEqual(adapter.clock_time(25 * 60 * 60 * 1000), time(1))
        self.assertEqual(adapter.epoch_millis(None), 0)

    def test_research_prediction_is_explicit_and_uses_original_formula_branches(self):
        calls = []
        def predictor(kind, inputs, state, native):
            calls.append((kind, native))
            state.start_done = True
            return 15
        controller = ResearchOptimizedStartStop(lead_predictor=predictor)
        state = controller.tick(starting(), now=at(1)).state
        self.assertEqual(calls, [("start", 81)])
        self.assertEqual(state.lead_time, 15)
        self.assertFalse(state.start_done)
        controller.tick(starting(space_temp_valid=False), now=at(1))
        controller.tick(stopping(space_temp=68), now=at(1))
        self.assertEqual(len(calls), 1)
        self.assertEqual(OptimizedStartStop().tick(starting(), now=at(1)).state.lead_time, 81)


class JavaDifferentialTests(unittest.TestCase):
    """Actual extracted Java under documented SDK stubs, never SDK certification."""

    def compare_trace(self, rows, config=None, initial=None, time_adapter=None):
        config = Config() if config is None else config
        controller = OptimizedStartStop(config, time_adapter=time_adapter)
        if initial:
            self.patch_state(controller.state, initial)
        try:
            java_config = asdict(config)
            if time_adapter is not None:
                java_config["zone_offset_minutes"] = int(time_adapter.local(EPOCH).utcoffset().total_seconds() / 60)
            expected = run_oracle(rows, config=java_config, initial_state=initial)
        except (JavaUnavailable, OracleSourceUnavailable) as error:
            self.skipTest(f"Java differential behavior NOT VERIFIED: {error}")
        # A provided original with a mismatching SHA remains a visible failure.
        trigger_counts = {"start": 0, "stop": 0}
        inputs = Inputs()
        current_now = EPOCH
        for index, (row, java) in enumerate(zip(rows, expected)):
            for key, value in row.get("config_patch", {}).items():
                if key == "now":
                    current_now = value
                elif key not in {"running", "steady_state", "zone_offset_minutes"}:
                    setattr(controller.config, key, value)
            self.patch_state(controller.state, row.get("state_patch", {}))
            for key, value in row.get("user_parameter_changes", {}).items():
                controller.user_parameter_changed(key + "_user_defined", value, now=row.get("state_patch", {}).get("now", current_now),
                                                  running=row.get("config_patch", {}).get("running", True),
                                                  steady_state=row.get("config_patch", {}).get("steady_state", True))
            if "now" in row:
                current_now = row["now"]
            for key, value in row.items():
                if key in Inputs.__dataclass_fields__:
                    setattr(inputs, key, value)
            result = controller.tick(inputs, now=current_now)
            actual = asdict(result.state)
            for event in result.events:
                if event["type"] == "trigger":
                    trigger_counts[event["kind"]] += 1
            actual.update({name + "_trigger_count": count for name, count in trigger_counts.items()})
            for key, value in java.items():
                observed = actual[key]
                if key in {"last_start_time", "last_stop_time", "parameter_reset_time"}:
                    observed = controller.time_adapter.epoch_millis(observed)
                    value = controller.time_adapter.epoch_millis(datetime.fromisoformat(value))
                elif key == "calculated_command_time":
                    observed = controller.time_adapter.clock_millis(observed)
                    value = controller.time_adapter.clock_millis(value)
                with self.subTest(tick=index, field=key):
                    if isinstance(value, float) and math.isnan(value):
                        self.assertTrue(math.isnan(observed))
                    else:
                        self.assertEqual(observed, value)

    @staticmethod
    def patch_state(state, patch):
        for key, value in patch.items():
            if key in {"start_time_command_status_flags", "stop_time_command_status_flags"}:
                getattr(state, key.removesuffix("_status_flags")).status_flags = value
            elif key in RATE_NAMES or key in {"space_temp_change", "observed_minutes_per_degree"}:
                setattr(state, key, float32(value))
            else:
                setattr(state, key, value)

    def test_native_start_partial_learning_stop_and_float_zero(self):
        rows = [dict(asdict(starting()), now=at(6, 39)),
                dict(asdict(starting()), now=at(6, 39, 15)),
                dict(asdict(starting(space_temp=60.001, schedule_status=True, next_event_value=False, next_event_time=at(18), stop_enable=True)), now=at(8)),
                dict(asdict(stopping()), now=at(17, 20, 15)),
                dict(asdict(stopping(space_temp=72 - 1e-9, schedule_status=False)), now=at(18))]
        self.compare_trace(rows)

    def test_independent_boundary_matrix(self):
        generator = random.Random(386_710)
        rows = []
        default = State()
        reset = {key: value for key, value in asdict(default).items()
                 if key not in {"start_time_command", "stop_time_command", "message"}}
        reset.update(start_time_command_status_flags=16, stop_time_command_status_flags=32)
        coefficients = [0, -1, 0.1, 10, 1e9, math.inf, -math.inf, math.nan]
        for index in range(300):
            patch = dict(reset)
            patch.update(program_mode=generator.randrange(5), last_program_mode=generator.randrange(5),
                         start_done=bool(generator.randrange(2)), analysis_complete=bool(generator.randrange(2)),
                         lead_time=generator.choice([0, 91, -31, 2**31 - 1]),
                         space_temp_at_beginning=generator.choice([60, 68, 72, 80]),
                         control_mode_at_beginning=bool(generator.randrange(2)),
                         last_start_time=at(6), last_stop_time=at(6))
            config = {key: generator.choice(coefficients) for key in RATE_NAMES}
            patch.update(config)
            config.update(old_parameter_multiplier=generator.choice([-1, 0, 2, 2**31 - 1]),
                          dynamic_parameter_adjust=bool(generator.randrange(2)))
            row = dict(now=at(generator.choice([0, 6, 7, 8, 15, 16, 17, 18]), generator.choice([0, 1, 30]), 15),
                       space_temp=generator.choice([60, 60 + 1e-9, 68, 72, 72 - 1e-9, 77, 80]),
                       outside_temp=generator.uniform(-10, 95),
                       next_event_time=at(generator.choice([8, 15, 18])) + timedelta(days=generator.choice([0, 0, 0, 1])),
                       start_enable=bool(generator.randrange(2)), stop_enable=bool(generator.randrange(2)),
                       schedule_status=bool(generator.randrange(2)), next_event_value=bool(generator.randrange(2)),
                       heat_cool_mode=bool(generator.randrange(2)), space_temp_valid=bool(generator.randrange(2)),
                       state_patch=patch, config_patch=config)
            rows.append(row)
        self.compare_trace(rows)

    def test_each_learning_direction_weight_and_user_callback(self):
        rows = []
        for mode, beginning, current, cooling in ((2, 80, 79.999, False), (2, 60, 60.001, True),
                                                  (4, 72, 71.999, False), (4, 72, 72.001, True)):
            for weight in (-1, 0, 2, 2**31 - 1):
                rows.append(dict(now=at(8), space_temp=current,
                                 next_event_time=at(18), start_enable=True, stop_enable=True,
                                 next_event_value=(mode == 2), schedule_status=(mode == 2), heat_cool_mode=cooling,
                                 state_patch=dict(program_mode=mode, last_program_mode=mode, start_done=True,
                                                  analysis_complete=False, control_mode_at_beginning=cooling,
                                                  last_start_time=at(7), last_stop_time=at(7), space_temp_at_beginning=beginning,
                                                  **{key: 10 for key in RATE_NAMES}),
                                 config_patch=dict(old_parameter_multiplier=weight)))
        rows.append(dict(now=at(9), state_patch=dict(now=at(9)), user_parameter_changes={"runtime_per_degree_heating": -2}))
        self.compare_trace(rows)

    def test_declared_fixed_timezone_date_and_null_stubs(self):
        rows = [dict(asdict(starting(next_event_time=at(8).replace(year=2025))), now=at(1)),
                dict(asdict(starting(next_event_time=at(8) + timedelta(days=1))), now=at(1)),
                dict(asdict(starting(next_event_time=None)), now=at(1)),
                dict(asdict(starting(next_event_time=EPOCH + timedelta(hours=8))), now=EPOCH + timedelta(hours=1)),
                dict(asdict(starting(next_event_time=at(8))), now=at(7))]
        self.compare_trace(rows, time_adapter=TimeAdapter(timezone(timedelta(hours=-6))))


if __name__ == "__main__":
    unittest.main()
