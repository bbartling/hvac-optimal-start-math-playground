# IoT/BAS driver

The core package imports with the Python standard library alone. It does not open sockets, write BACnet/MQTT points, start services or submit competition runs. A real IO adapter owns sensor acquisition, status translation, clock delivery and command links.

Run the JSONL interface from the repository or an installed package:

```powershell
Get-Content events.jsonl | python -m hvac_optimal iot
```

Each device has an independent controller, four learned parameters and fixed zone sampler. Configure it once:

```json
{"event":"configure","device":"AHU-1","station_timezone":"America/Chicago","zones":["E1","E2","I1","I2"],"zone_types":{"E1":"exterior","E2":"exterior","I1":"interior","I2":"interior"},"sample_fraction":0.3}
```

An IANA timezone uses the host timezone database (or installed `tzdata` on hosts without one). The default is explicitly UTC, not guessed from the machine. Send aware timestamps. `zone_types` is supplied metadata, not inferred from the example IDs; names may be arbitrary.

```json
{"device":"AHU-1","now":"2026-11-18T05:50:15-06:00","zone_temperatures":{"E1":66,"E2":66.2,"I1":66.1,"I2":66.3},"inputs":{"start_enable":true,"stop_enable":true,"space_temp_valid":true,"schedule_status":false,"next_event_time":"2026-11-18T06:00:00-06:00","next_event_value":true,"outside_temp":35,"heat_cool_mode":false}}
```

Alternatively, provide `inputs.space_temp` directly when an existing BAS point already performs averaging. With a configured sampler, the default selection is 30%, balanced exterior/interior where classification permits; numeric averaging weights default to equal. Missing selected sensors cause an explicit transport/input error, not silent resampling or substituted temperatures. Preserve actual BAS validity through `space_temp_valid`; the driver invents no minimum-change or training-quality threshold.

Native command interpretation:

| Output | Value | Null status | Meaning |
| --- | --- | --- | --- |
| start | true | false | active optimized start |
| stop | false | false | active optimized stop |
| either | false | true | no override; normal schedule/sequence remains responsible |

Preserve both value and status when wiring the block. Clearing a null flag is not equivalent to writing a boolean false into a downstream actuator. The original Java's trigger actions depend on external links; this package returns receipts rather than assuming a plant wiring.

The caller should deliver the reference minute scans at `:15`; `next_clock_ticket()` supplies that schedule. The notebook/simulator's five-minute adapter is explicitly quantized and not an identical field runtime. Calling `tick` manually does not impose a new debounce interval.

Native user-defined rate changes use an explicit message:

```json
{"event":"user_parameter","device":"AHU-1","now":"2026-11-18T07:00:15-06:00","name":"runtimePerDegreeHeatingUserDefined","value":10,"running":true,"steady_state":true}
```

This copies the selected rate and records reset metadata according to the source; it does not reset the control latches. Malformed packets emit error receipts and a nonzero CLI exit status. Nonfinite native numeric results use explicit string tokens in JSON rather than being clipped to a plausible rate.

Verified-unoccupied prestart commonly requests full recirculation via the external minimum-outside-air damper command, then restores occupied ventilation. Existing site interlocks remain responsible. That ventilation command is outside this start/stop class and is not a new learning gate. The competition can only provide up to 70% recirculation.

The driver is tested software, not a completed Niagara runtime replacement, MicroPython port, field commissioning or certification. Keep research predictor selection separate from the native reference and validate the IO adapter against actual site clock/status/link semantics.
