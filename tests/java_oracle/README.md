# Extracted Java differential oracle

`runner.run_oracle(trace, config=None, initial_state=None)` compiles a small
wrapper around methods mechanically extracted from the owner-supplied
`BOptimizedStartStop.java`. Method declarations and bodies are copied unchanged
by brace matching at test runtime. The original proprietary class is not
bundled or published by this repository. Its expected SHA256 is checked before
extraction; the digest is recorded in `runner.py` and the reference contract.

Set `HVAC_VENDOR_JAVA_SOURCE` to the local original file. On the owner's Windows
machine, the default is `~/Downloads/BOptimizedStartStop.java`. A JDK (tested
with JDK 11) must provide `java` and `javac` on `PATH`. A missing JDK raises
`JavaUnavailable`, which a test may explicitly skip. Missing or changed source
raises an error with instructions; it is not silently accepted or skipped.

Generated Java, class files and temporary trace products are created under
the operating system's TEMP directory and removed when a trace completes.
Only Python standard-library modules are used. To avoid repository bytecode
caches when running tests, set `PYTHONDONTWRITEBYTECODE=1` or use `python -B`.

Trace rows use the Python port's snake_case input fields plus `now` (an ISO
datetime or `datetime`). They also accept `state_patch`, `config_patch`, and
`user_parameter_changes` dictionaries before each tick. Configuration and
initial state may be mappings or dataclass instances. Rate changes use native
rate names or their `_user_defined` variants. The original `changed` callback
is extracted too; `running` and `steady_state` patches exercise its two guards.
All clock reads within one tick receive the same injected `now`.

Outputs flatten native state and all four coefficients; command values, null
bits and other status bits remain distinct. Time-of-day outputs use ISO time;
absolute outputs use UTC ISO datetime. Java NULL timestamps are represented
as the epoch and must be normalized against initial Python `None` timestamps.
Extra outputs record cumulative trigger counts and parameter-reset time.
Message strings are deliberately excluded from differential comparison.
NaN and infinities are parsed as Python floats and need NaN-aware comparisons.

## What these tests establish

The compiler executes the original expressions, state transitions, arithmetic,
eligibility checks, latches and command mutations against these declared
substitutes. This detects Python translation errors without rewriting the Java
algorithm in the oracle. It does **not** execute or certify Niagara.

The SDK substitutes use epoch milliseconds; a fixed station offset (UTC by
default, or `zone_offset_minutes` in a patch); NULL = epoch zero; relative
minutes truncated toward zero; `delta(other) = other - this`; modulo-24-hour
time-of-day construction; strict before/after comparisons; explicit numeric
status validity; separate output null and other-status fields; immediate empty
trigger handlers that count invocations; and a held clock inside each tick.
Property callbacks for the user-defined reset path run synchronously here.
They do not establish vendor status masks, actual NULL/time overflow semantics,
DST behavior, action queues, scheduler behavior, external links, persistence,
or field performance. Those require SDK/runtime evidence.
