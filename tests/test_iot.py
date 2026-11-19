import io
import json

from hvac_optimal.iot import IoTDriver, run_jsonl


def packet(device="AHU-1", **updates):
    result = {"device": device, "now": "2026-11-18T05:50:15Z", "inputs": {
        "space_temp": 66, "outside_temp": 35, "start_enable": True,
        "next_event_time": "2026-11-18T06:00:00Z", "next_event_value": True}}
    result.update(updates)
    return result


def test_driver_preserves_start_and_null_stop_status():
    driver = IoTDriver()
    result = driver.process(packet())
    assert result["state"]["program_mode"] == 2
    assert result["state"]["start_time_command"] == {"value": True, "status_null": False, "status_flags": 0}
    assert result["state"]["stop_time_command"]["status_null"] is True


def test_devices_have_independent_native_rates_and_callbacks():
    seen = []
    driver = IoTDriver(on_result=seen.append)
    driver.process(packet())
    driver.process(packet("AHU-2"))
    result = driver.process({"device": "AHU-1", "event": "user_parameter", "now": "2026-11-18T05:51:15Z",
                             "name": "runtimePerDegreeHeatingUserDefined", "value": 21})
    assert result["applied"] is True
    assert driver.controllers["AHU-1"].state.runtime_per_degree_heating == 21
    assert driver.controllers["AHU-2"].state.runtime_per_degree_heating == 10
    seen[0]["state"]["program_mode"] = 99
    assert driver.controllers["AHU-1"].state.program_mode != 99


def test_active_stop_is_false_but_not_null():
    driver = IoTDriver()
    result = driver.process(packet(now="2026-11-18T17:50:15Z", inputs={
        "space_temp": 70, "stop_enable": True, "schedule_status": True,
        "next_event_time": "2026-11-18T18:00:00Z", "next_event_value": False,
        "heat_cool_mode": False}))
    assert result["state"]["program_mode"] == 4
    assert result["state"]["stop_time_command"]["value"] is False
    assert result["state"]["stop_time_command"]["status_null"] is False


def test_jsonl_bad_packet_does_not_change_or_suppress_next_tick():
    output = io.StringIO()
    code = run_jsonl(["not-json", json.dumps(packet())], output)
    receipts = [json.loads(line) for line in output.getvalue().splitlines()]
    assert code == 1
    assert receipts[0]["event"] == "transport_error"
    assert receipts[1]["state"]["program_mode"] == 2


def test_balanced_zone_input_keeps_tiny_native_partial_update_eligible():
    driver = IoTDriver()
    zones = [f"zone-{n}" for n in range(10)]
    driver.process({"event": "configure", "device": "AHU-1", "zones": zones,
                    "zone_types": {z: "exterior" if i < 5 else "interior" for i, z in enumerate(zones)}})
    before = packet(zone_temperatures={z: 66.0 for z in zones})
    result = driver.process(before)
    assert result["sampling"]["selected_zone_count"] == 3
    assert result["sampling"]["balance_achieved"] is True
    after = packet(now="2026-11-18T06:00:15Z", zone_temperatures={z: 66.001 for z in zones}, inputs={
        "start_enable": True, "schedule_status": True, "next_event_value": False,
        "next_event_time": "2026-11-18T18:00:00Z"})
    result = driver.process(after)
    assert result["state"]["runtime_per_degree_heating"] > 1000
    assert any(e["type"] == "native_learning" for e in result["events"])
