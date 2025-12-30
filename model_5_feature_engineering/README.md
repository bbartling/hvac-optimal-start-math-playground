# VAV + Outside Air Dataset

### (Imperial Units, Brick-Style Labels)

Cleaned dataset file: **`vav_oat_brick_clean.csv`**

---

## 📌 Columns

* `timestamp` — naive local datetime at ~5-minute resolution
* `t_minutes` — integer minute index derived from Excel time
* `Excel Time` — original Excel serial timestamp
* `brick:Outside_Air_Temperature_Sensor_degF`
* `brick:Zone_Air_Temperature_Sensor_degF`
* `brick:Zone_Air_Temperature_Cooling_Setpoint_degF`
* `brick:Zone_Air_Temperature_Heating_Setpoint_degF`
* `brick:Discharge_Air_Temperature_Sensor_degF`
* `brick:Discharge_Air_Temperature_Sensor_2_degF`
* `brick:Discharge_Air_Flow_Setpoint_cfm`
* `brick:Discharge_Air_Flow_Sensor_cfm`
* `brick:Zone_Air_Static_Pressure_Sensor_inH2O`
* `brick:Zone_Air_Humidity_Sensor_percent`
* `brick:Reheat_Valve_Command_percent`
* `brick:Door_Status`

---

## ⚙️ Quickstart

Install dependencies:

```bash
pip install pandas matplotlib numpy
```

---

## 🧠 Zone Recovery Logic

```python
# Determine mode + ΔT
if zt > cool_sp:
    mode_heating = 0
    deltaT = abs(zt - cool_sp)
elif zt < heat_sp:
    mode_heating = 1
    deltaT = abs(zt - heat_sp)
else:
    # Zone already within band between heat and cool setpoints -> skip
    continue
```

Meaning:

**If zone temp is ABOVE cooling setpoint**
→ Cooling startup
→ Record ΔT relative to cooling setpoint
→ Event recorded

**If zone temp is BELOW heating setpoint**
→ Heating startup
→ Record ΔT relative to heating setpoint
→ Event recorded

**If zone temp is BETWEEN heating + cooling setpoints**
→ Already comfortable
→ No recovery needed
→ Event skipped

---

# HVAC Startup Recovery Dataset

Each **row = one HVAC startup event** where:

* HVAC was OFF
* HVAC turned ON
* Zone was **not already comfortable**
* HVAC remained ON until reaching occupied setpoint
* We captured:

  * how far the zone was from setpoint (ΔT)
  * outdoor air conditions
  * recovery time
  * calendar context (day-of-week, ML-ready)

---

## 📊 Columns

| Column              | Meaning                                                     |
| ------------------- | ----------------------------------------------------------- |
| `start_time`        | Timestamp when HVAC turned ON                               |
| `mode_heating`      | 1 = heating recovery, 0 = cooling recovery                  |
| `oat_start_degF`    | Outside air temperature at startup                          |
| `deltaT_start_degF` | Degrees from setpoint at startup (“how wrong” the zone was) |
| `recovery_minutes`  | Time until comfort restored (while HVAC stayed ON)          |
| `dow_1 … dow_6`     | One-hot weekday encoding (Monday baseline)                  |

---

## 🧾 Example Interpretation

```
2025-01-11 07:25:00
mode_heating = 1
OAT = 42.7°F
ΔT = 0.2°F
Recovery = 20 min
dow_* = 0
```

→ Heating startup
→ Cold morning
→ Small error but required heat
→ 20-minute recovery
→ Day-of-week currently encoded as baseline

---

## ❗ Note About `dow_*`

Current rows show:

```
dow_1,dow_2,dow_3,dow_4,dow_5,dow_6
0,0,0,0,0,0
```

This **does not mean Monday**.
It means all recorded events so far occurred on one weekday, and due to `drop_first=True`, the category collapses to baseline. Once events occur on multiple weekdays, columns will activate normally.

