"""Compile extracted Java control methods in TEMP and run fixed-clock traces.

This compares language-level behavior under declared SDK substitutes. It does
not execute Niagara, copy the owner's class into the repository, or certify
the SDK substitutes. Only the Python standard library and a JDK are used.
"""
from __future__ import annotations

import dataclasses
from datetime import datetime, time, timezone
import hashlib
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from typing import Any, Iterable, Mapping


SOURCE_SHA256 = "0F2B759951F18DEC2BA05C09D8B03569C90C0D69B3BB08CC18FFB9009FE3A539"
METHODS = (
    "changed", "formatNumeric", "doCalculate", "performStartStopCalculation",
    "performStartCalculation", "performStopCalculation", "performStartStopControl",
    "updateControlOutput", "performStartStopAnalysis", "handleStartAnalysis",
    "isCoolingAnalysis", "handleStopAnalysis",
)
RATE_NAMES = (
    "runtime_per_degree_cooling", "runtime_per_degree_heating",
    "drifttime_per_degree_cooling", "drifttime_per_degree_heating",
)


class JavaUnavailable(RuntimeError):
    """A JDK is unavailable; callers may explicitly skip Java-only tests."""


class OracleSourceUnavailable(RuntimeError):
    """Supply the owner's original source locally to run these tests."""


def _mapping(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if dataclasses.is_dataclass(value):
        return dataclasses.asdict(value)
    return dict(value)


def _camel(name: str) -> str:
    head, *tail = name.split("_")
    return head + "".join(word.title() for word in tail)


def _extract_method(source: str, name: str) -> str:
    """Copy one whole declaration without translating its expressions/guards."""
    match = re.search(r"(?m)^\s+(?:public|private)\s+[^\n;{}]+\b" + re.escape(name) + r"\([^\n]*\)\s*\{", source)
    if not match:
        raise ValueError(f"Original Java method {name!r} was not found")
    begin = source.index("{", match.start())
    depth, quoted, escaped = 1, None, False
    index = begin + 1
    while depth:
        if index >= len(source):
            raise ValueError(f"Unbalanced braces extracting {name}")
        char = source[index]
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quoted:
                quoted = None
        elif char in ('"', "'"):
            quoted = char
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
        index += 1
    return source[match.start():index]


def _source_path() -> Path:
    configured = os.environ.get("HVAC_VENDOR_JAVA_SOURCE")
    return Path(configured) if configured else Path.home() / "Downloads" / "BOptimizedStartStop.java"


def _read_source() -> str:
    path = _source_path()
    if not path.is_file():
        raise OracleSourceUnavailable(
            f"Original owner-supplied Java is absent: {path}. Set HVAC_VENDOR_JAVA_SOURCE; "
            "the proprietary class is intentionally not bundled."
        )
    blob = path.read_bytes()
    actual = hashlib.sha256(blob).hexdigest().upper()
    if actual != SOURCE_SHA256:
        raise ValueError(f"Java source SHA256 changed: expected {SOURCE_SHA256}, got {actual}")
    return blob.decode("utf-8-sig")


def _getter_declarations() -> str:
    fields: dict[str, tuple[str, str]] = {
        "heatCoolMode": ("BStatusBoolean", "new BStatusBoolean(false)"),
        "startEnable": ("BStatusBoolean", "new BStatusBoolean(false)"),
        "stopEnable": ("BStatusBoolean", "new BStatusBoolean(false)"),
        "scheduleStatus": ("BStatusBoolean", "new BStatusBoolean(false)"),
        "nextEventValue": ("BStatusBoolean", "new BStatusBoolean(false)"),
        "spaceTemp": ("BStatusNumeric", "new BStatusNumeric()"),
        "outsideTemp": ("BStatusNumeric", "new BStatusNumeric()"),
        "spaceTempAtBeginning": ("BStatusNumeric", "new BStatusNumeric()"),
        "outsideTempAtBeginning": ("BStatusNumeric", "new BStatusNumeric()"),
        "startTimeCommand": ("BStatusBoolean", "new BStatusBoolean(false, true)"),
        "stopTimeCommand": ("BStatusBoolean", "new BStatusBoolean(false, true)"),
        "message": ("BStatusString", "new BStatusString()"),
        "nextEventTime": ("BAbsTime", "BAbsTime.NULL"),
        "lastStartTime": ("BAbsTime", "BAbsTime.NULL"),
        "lastStopTime": ("BAbsTime", "BAbsTime.NULL"),
        "parameterResetTime": ("BAbsTime", "BAbsTime.NULL"),
        "calculatedCommandTime": ("BTime", "new BTime(0)"),
        "earliestStartTime": ("BTime", "new BTime(10000)"),
        "earliestStopTime": ("BTime", "new BTime(57600000)"),
        "upperComfortLimit": ("float", "77.0F"),
        "lowerComfortLimit": ("float", "68.0F"),
        "oldParameterMultiplier": ("int", "2"),
        "dynamicParameterAdjust": ("boolean", "true"),
        "programMode": ("int", "0"),
    }
    for rate in RATE_NAMES:
        fields[_camel(rate)] = ("float", "10.0F")
        fields[_camel(rate) + "UserDefined"] = ("float", "0.0F")
    declarations = []
    for name, (kind, default) in fields.items():
        cap = name[0].upper() + name[1:]
        storage = "value" + cap if name.endswith("UserDefined") else name
        declarations.extend((
            f"public {kind} {storage} = {default};",
            f"public {kind} get{cap}() {{ return {storage}; }}",
            f"public void set{cap}({kind} value) {{ {storage} = value; }}",
        ))
    return "\n".join(declarations)


def _java_source(original: str) -> str:
    declarations = _getter_declarations()
    methods = "\n".join(_extract_method(original, name) for name in METHODS)
    return _JAVA.replace("/* PROPERTY_ACCESSORS */", declarations).replace("/* ORIGINAL_METHODS */", methods)


def _scalar(value: Any, *, clock: bool = False, tod: bool = False) -> str:
    if clock:
        if value is None:
            return "0"
        if isinstance(value, str):
            value = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if isinstance(value, datetime):
            if value.tzinfo is None:
                value = value.replace(tzinfo=timezone.utc)
            epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
            delta = value.astimezone(timezone.utc) - epoch
            return str(delta.days * 86400000 + delta.seconds * 1000 + delta.microseconds // 1000)
    if tod:
        if isinstance(value, str):
            value = time.fromisoformat(value)
        if isinstance(value, time):
            return str(((value.hour * 60 + value.minute) * 60 + value.second) * 1000 + value.microsecond // 1000)
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, float):
        if math.isnan(value):
            return "NaN"
        if math.isinf(value):
            return "Infinity" if value > 0 else "-Infinity"
    return str(value)


_ABS_TIMES = {"now", "next_event_time", "last_start_time", "last_stop_time", "parameter_reset_time"}
_TOD_TIMES = {"earliest_start_time", "earliest_stop_time", "calculated_command_time"}


def _fields(values: Mapping[str, Any]) -> list[str]:
    result = []
    for name, value in values.items():
        if name == "input_statuses":
            # Python adapter metadata; the extracted class ignores these.
            continue
        if name in {"message", "input_statuses"}:
            continue
        if name in {"start_time_command", "stop_time_command"} and isinstance(value, Mapping):
            result.extend((name, _scalar(value.get("value", False))))
            for status in ("status_null", "status_flags"):
                if status in value:
                    result.extend((name + "_" + status, _scalar(value[status])))
        elif name in {"rates", "coefficients"}:
            result.extend(_fields(_mapping(value)))
        else:
            result.extend((name, _scalar(value, clock=name in _ABS_TIMES, tod=name in _TOD_TIMES)))
    return result


def _iso_epoch(value: int) -> str:
    return datetime.fromtimestamp(value / 1000, tz=timezone.utc).isoformat()


def _parse_output(line: str) -> dict[str, Any]:
    pairs = line.split("\t")
    raw = dict(zip(pairs[::2], pairs[1::2]))
    result: dict[str, Any] = {}
    booleans = {"start_done", "analysis_complete", "control_mode_at_beginning"}
    integers = {"program_mode", "last_program_mode", "lead_time", "optimized_runtime_minutes", "start_trigger_count", "stop_trigger_count"}
    for name, value in raw.items():
        if name in booleans:
            result[name] = value == "true"
        elif name in integers:
            result[name] = int(value)
        elif name in {"start_time_command", "stop_time_command"}:
            val, null, flags = value.split(",")
            result[name] = {"value": val == "true", "status_null": null == "true", "status_flags": int(flags)}
        elif name in {"last_start_time", "last_stop_time", "parameter_reset_time"}:
            result[name] = _iso_epoch(int(value))
        elif name == "calculated_command_time":
            milliseconds = int(value)
            seconds, millis = divmod(milliseconds, 1000)
            hours, seconds = divmod(seconds, 3600)
            minutes, seconds = divmod(seconds, 60)
            result[name] = f"{hours:02}:{minutes:02}:{seconds:02}" + (f".{millis:03}" if millis else "")
        else:
            result[name] = float(value)
    return result


def run_oracle(
    trace: Iterable[Mapping[str, Any]],
    config: Mapping[str, Any] | Any | None = None,
    initial_state: Mapping[str, Any] | Any | None = None,
) -> list[dict[str, Any]]:
    """Run one trace with extracted source, returning flattened state records.

    Rows accept input fields plus ``state_patch`` (applied before that tick),
    ``config_patch`` and ``user_parameter_changes``. Changes use the active rate
    names, e.g. ``runtime_per_degree_heating``. ``running`` and ``steady_state``
    in patches control the two guards on the original ``changed`` callback.
    Clock fields are ISO datetime strings or datetime objects; naive means UTC.
    Time-of-day fields are ISO time strings or time objects. All values are
    interpreted in the declared fixed station offset (UTC by default).
    """
    javac, java = shutil.which("javac"), shutil.which("java")
    if not javac or not java:
        raise JavaUnavailable("Java differential tests require java and javac on PATH (JDK 11+)")
    original = _read_source()
    lines = []
    for command, values in (("C", _mapping(config)), ("S", _mapping(initial_state))):
        if values:
            lines.append("\t".join([command] + _fields(values)))
    count = 0
    for row in trace:
        values = _mapping(row)
        for key, command in (("config_patch", "C"), ("state_patch", "S")):
            patch = values.pop(key, None)
            if patch:
                lines.append("\t".join([command] + _fields(_mapping(patch))))
        changes = values.pop("user_parameter_changes", None)
        if changes:
            if "now" in values:
                lines.append("\t".join(["C", "now", _scalar(values["now"], clock=True)]))
            lines.append("\t".join(["U"] + _fields(_mapping(changes))))
        lines.append("\t".join(["T"] + _fields(values)))
        count += 1
    # Both source extraction products and javac output remain outside the repo.
    with tempfile.TemporaryDirectory(prefix="hvac-java-oracle-") as directory:
        path = Path(directory)
        (path / "Oracle.java").write_text(_java_source(original), encoding="utf-8")
        build = subprocess.run([javac, "-encoding", "UTF-8", "-d", directory, str(path / "Oracle.java")],
                               text=True, capture_output=True, timeout=60)
        if build.returncode:
            raise RuntimeError("Extracted Java oracle failed to compile:\n" + build.stderr)
        run = subprocess.run([java, "-cp", directory, "Oracle"], input="\n".join(lines) + "\n",
                             text=True, capture_output=True, timeout=60)
        if run.returncode:
            raise RuntimeError("Extracted Java oracle failed:\n" + run.stderr)
        records = [_parse_output(line) for line in run.stdout.splitlines() if line]
        if len(records) != count:
            raise RuntimeError(f"Oracle returned {len(records)} records for {count} ticks")
        return records


_JAVA = r'''
import java.io.*;
import java.lang.reflect.*;
import java.text.DecimalFormat;
import java.time.*;
import java.util.*;

// Deliberately small, documented SDK substitutes, NOT vendor SDK classes.
class BRelTime {
  final long millis;
  BRelTime(long value) { millis = value; }
  static BRelTime make(long value) { return new BRelTime(value); }
  int getMinutes() { return (int)(millis / 60000L); }
}
class BTime {
  final long millis;
  BTime(long value) { millis = Math.floorMod(value, 86400000L); }
  static BTime make(BAbsTime value) { return new BTime(value.getTimeOfDayMillis()); }
  static BTime make(BRelTime value) { return new BTime(value.millis); }
  long getTimeOfDayMillis() { return millis; }
  boolean isBefore(BTime other) { return millis < other.millis; }
  boolean isAfter(BTime other) { return millis > other.millis; }
}
class BAbsTime {
  static final BAbsTime NULL = new BAbsTime(0L);
  final long millis;
  BAbsTime(long value) { millis = value; }
  ZonedDateTime local() { return Instant.ofEpochMilli(millis).atZone(Clock.zone); }
  int getDayOfYear() { return local().getDayOfYear(); }
  long getTimeOfDayMillis() { return local().toLocalTime().toNanoOfDay()/1000000L; }
  BRelTime delta(BAbsTime other) { return new BRelTime(other.millis - millis); }
  public String toString() { return Instant.ofEpochMilli(millis).toString(); }
}
class Clock {
  static BAbsTime now = BAbsTime.NULL;
  static ZoneOffset zone = ZoneOffset.UTC;
  static BAbsTime time() { return now; }
}
class Status {
  boolean valid = true;
  boolean isValid() { return valid; }
}
class BStatusNumeric {
  double value = 0;
  Status status = new Status();
  double getValue() { return value; }
  void setValue(double value) { this.value = value; }
  Status getStatus() { return status; }
}
class BStatusBoolean {
  boolean value, statusNull = false;
  int statusFlags = 0;
  BStatusBoolean(boolean value) { this.value = value; }
  BStatusBoolean(boolean value, boolean isNull) { this.value = value; statusNull = isNull; }
  boolean getValue() { return value; }
  void setValue(boolean value) { this.value = value; }
  void setStatusNull(boolean value) { statusNull = value; }
  public String toString() { return value + "," + statusNull + "," + statusFlags; }
}
class BStatusString { String value = ""; void setValue(String value) { this.value = value; } }
class Property {
  final String name;
  Property(String value) { name = value; }
  public boolean equals(Object other) { return other instanceof Property && name.equals(((Property)other).name); }
  public int hashCode() { return name.hashCode(); }
}
class Context {}
class Sys { static boolean steadyState = true; static boolean atSteadyState() { return steadyState; } }
class BComponent {
  boolean running = true;
  public void changed(Property property, Context context) {}
  public boolean isRunning() { return running; }
}
public class Oracle extends BComponent {
  static final boolean ACTIVE=true, INACTIVE=false, START=true, STOP=false, DISABLED=false, ENABLED=true, COOLING=true, HEATING=false;
  static final long TIME_00_01=60000L;
  static final int NO_CALCULATION=0, START_CALCULATION=1, START_IN_PROCESS=2, STOP_CALCULATION=3, STOP_IN_PROCESS=4;
  static final Property drifttimePerDegreeCoolingUserDefined = new Property("drifttimePerDegreeCoolingUserDefined");
  static final Property drifttimePerDegreeHeatingUserDefined = new Property("drifttimePerDegreeHeatingUserDefined");
  static final Property runtimePerDegreeCoolingUserDefined = new Property("runtimePerDegreeCoolingUserDefined");
  static final Property runtimePerDegreeHeatingUserDefined = new Property("runtimePerDegreeHeatingUserDefined");
  static final DummyLog ossLog = new DummyLog();
  static class DummyLog { void trace(String value) {} }
  Oracle getParent() { return this; }
  String getName() { return "oracle"; }
  boolean controlModeAtBeginning=false, startDone=false, analysisComplete=false;
  float observedMinutesPerDegree=0.0F, spaceTempChange=0.0F;
  int leadTime=0, optimizedRuntimeMinutes=0, lastProgramMode=0;
  int startTriggerCount=0, stopTriggerCount=0;
  BAbsTime now=BAbsTime.NULL;
  void startTimeTrigger() { startTriggerCount++; }
  void stopTimeTrigger() { stopTriggerCount++; }
  /* PROPERTY_ACCESSORS */
  /* ORIGINAL_METHODS */

  static String camel(String snake) {
    StringBuilder out=new StringBuilder(); boolean upper=false;
    for(char c:snake.toCharArray()) { if(c=='_') upper=true; else { out.append(upper ? Character.toUpperCase(c) : c); upper=false; } }
    return out.toString();
  }
  void apply(String name,String value) throws Exception {
    if(name.equals("now")) { Clock.now=new BAbsTime(Long.parseLong(value)); return; }
    if(name.equals("zone_offset_minutes")) { Clock.zone=ZoneOffset.ofTotalSeconds(Integer.parseInt(value)*60); return; }
    if(name.equals("steady_state")) { Sys.steadyState=Boolean.parseBoolean(value); return; }
    if(name.equals("running")) { running=Boolean.parseBoolean(value); return; }
    if(name.endsWith("_valid")) {
      String base=name.substring(0,name.length()-6);
      Object status=getClass().getField(camel(base)).get(this);
      if(status instanceof BStatusNumeric) ((BStatusNumeric)status).status.valid=Boolean.parseBoolean(value);
      return; // non-space statuses are deliberately unused by the original.
    }
    if(name.endsWith("_status_flags") || name.endsWith("_status_null")) {
      boolean flags=name.endsWith("_status_flags");
      String base=name.substring(0,name.length()-(flags ? 13 : 12));
      BStatusBoolean status=(BStatusBoolean)getClass().getField(camel(base)).get(this);
      if(flags) status.statusFlags=Integer.parseInt(value); else status.statusNull=Boolean.parseBoolean(value);
      return;
    }
    String fieldName=camel(name);
    if(fieldName.endsWith("UserDefined")) fieldName="value"+Character.toUpperCase(fieldName.charAt(0))+fieldName.substring(1);
    Field field=getClass().getDeclaredField(fieldName);
    Class<?> type=field.getType();
    if(type==boolean.class) field.setBoolean(this,Boolean.parseBoolean(value));
    else if(type==int.class) field.setInt(this,Integer.parseInt(value));
    else if(type==float.class) field.setFloat(this,Float.parseFloat(value));
    else if(type==BAbsTime.class) field.set(this,new BAbsTime(Long.parseLong(value)));
    else if(type==BTime.class) field.set(this,new BTime(Long.parseLong(value)));
    else if(type==BStatusNumeric.class) ((BStatusNumeric)field.get(this)).setValue(Double.parseDouble(value));
    else if(type==BStatusBoolean.class) ((BStatusBoolean)field.get(this)).setValue(Boolean.parseBoolean(value));
    else throw new IllegalArgumentException("Unsupported oracle field "+name);
  }
  void userChange(String name,String value) throws Exception {
    String fieldName=camel(name);
    if(!fieldName.endsWith("UserDefined")) fieldName += "UserDefined";
    String storage="value"+Character.toUpperCase(fieldName.charAt(0))+fieldName.substring(1);
    getClass().getDeclaredField(storage).setFloat(this,Float.parseFloat(value));
    changed(new Property(fieldName),null);
  }
  void output() {
    LinkedHashMap<String,Object> values=new LinkedHashMap<>();
    values.put("program_mode",programMode); values.put("last_program_mode",lastProgramMode);
    values.put("start_done",startDone); values.put("analysis_complete",analysisComplete);
    values.put("control_mode_at_beginning",controlModeAtBeginning); values.put("lead_time",leadTime);
    values.put("optimized_runtime_minutes",optimizedRuntimeMinutes); values.put("space_temp_change",(double)spaceTempChange);
    values.put("observed_minutes_per_degree",(double)observedMinutesPerDegree);
    values.put("runtime_per_degree_cooling",(double)runtimePerDegreeCooling);
    values.put("runtime_per_degree_heating",(double)runtimePerDegreeHeating);
    values.put("drifttime_per_degree_cooling",(double)drifttimePerDegreeCooling);
    values.put("drifttime_per_degree_heating",(double)drifttimePerDegreeHeating);
    values.put("calculated_command_time",calculatedCommandTime.millis);
    values.put("last_start_time",lastStartTime.millis); values.put("last_stop_time",lastStopTime.millis);
    values.put("parameter_reset_time",parameterResetTime.millis);
    values.put("space_temp_at_beginning",spaceTempAtBeginning.value);
    values.put("outside_temp_at_beginning",outsideTempAtBeginning.value);
    values.put("start_time_command",startTimeCommand); values.put("stop_time_command",stopTimeCommand);
    values.put("start_trigger_count",startTriggerCount); values.put("stop_trigger_count",stopTriggerCount);
    StringJoiner out=new StringJoiner("\t");
    for(Map.Entry<String,Object> item:values.entrySet()) { out.add(item.getKey()); out.add(item.getValue().toString()); }
    System.out.println(out.toString());
  }
  public static void main(String[] args) throws Exception {
    Locale.setDefault(Locale.US);
    Oracle oracle=new Oracle();
    BufferedReader input=new BufferedReader(new InputStreamReader(System.in));
    String line;
    while((line=input.readLine())!=null) {
      if(line.isEmpty()) continue;
      String[] fields=line.split("\t",-1);
      for(int i=1;i<fields.length;i+=2) {
        if(fields[0].equals("U")) oracle.userChange(fields[i],fields[i+1]);
        else oracle.apply(fields[i],fields[i+1]);
      }
      if(fields[0].equals("T")) { oracle.doCalculate(); oracle.output(); }
    }
  }
}
'''
