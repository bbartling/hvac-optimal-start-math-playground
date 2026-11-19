# Fixed zone sampling and the weighted AHU input

Each AHU receives its own explicit list of mapped zone IDs, fixed zone sampler,
BAS reference controller state, and estimator state. The mapping is authoritative:
zone-name prefixes are never used to guess membership. No whole-building
average is substituted for the individual AHU input.

`ZoneSampler` in `hvac_optimal/sampling.py` uses only the Python standard library.
By default it selects `ceil(0.30 * mapped_zone_count)` zones, with at least one
for every nonempty AHU inventory. This is a fixed sample for the run, not a fresh
sample on each reading or each day. Small inventories can therefore have an
actual sampling fraction greater than 30%; the receipt reports it.

Selection and weighting are separate operations:

1. Sort the explicit zone inventory; derive a SHA-256 seed from the run seed
   and AHU ID; use an isolated `random.Random` instance to sample without
   replacement. When explicit exterior and interior labels are both available,
   allocate the selected slots as evenly as their available group sizes allow.
   An odd extra slot is chosen deterministically from the seed. Redistribute
   slots when one group is too small. Sorting the selected result also fixes
   its arithmetic order.
2. On every reading, calculate `sum(weight * temperature) / sum(weight)` using
   exactly those selected zones. Every selected zone has a positive fixed
   weight. Unspecified weights are 1, so the default is the equal-weight mean
   of the selected sample. Weights are generic configuration; they are not
   asserted to be floor area, people count or airflow.

Zone selection is stable across processes and inventory permutations, independent
of Python's randomized `hash()` seed. The selection receipt records the algorithm
and seed. Persist explicit selected IDs when reproducing a field configuration
or moving across Python runtime versions; no cross-version guarantee for
`random.sample` implementation changes is claimed.

```python
from hvac_optimal.sampling import ZoneSampler

ahu_zones = {
    "AHU-1": ["room-A", "room-B", "room-C", "room-D", "room-E", "room-F"],
    "AHU-2": ["workshop", "lobby"],
}
samplers = {
    ahu: ZoneSampler(
        ahu, zones, fraction=0.30, seed="experiment-1",
        zone_types=zone_classification_for_this_ahu[ahu],
    )
    for ahu, zones in ahu_zones.items()
}

# Each AHU has its own sampler and its own existing BAS controller instance.
mean = samplers["AHU-1"].read(temperatures_by_zone_id)
# Pass mean to that AHU's BAS temperature input without changing units.
selection = samplers["AHU-1"].selection_receipt()
mean, same_selection = samplers["AHU-1"].read(
    temperatures_by_zone_id, with_receipt=True
)
```

`zone_types` is explicit metadata mapping each mapped zone ID to `exterior`,
`interior`, or `unknown`. Missing metadata is `unknown`; sensor names are never
used to infer a type. When both known groups can fill the sample, select from
those groups. If their combined inventory is too small, select all known zones
and fill the remaining slots from unknown zones. When only one known group
exists, or no types are known, use a deterministic uniform sample of the
explicit AHU inventory and identify that fallback. Do not present that sample
as balanced. Metadata extraction belongs to the building/simulator adapter,
which must supply classifications from actual metadata.

The receipt exposes `classification_coverage`, `classification_counts`,
`unknown_count`, `selected_group_counts`, `balance_applied`, `balance_achieved`,
and `fallback_reason`. A capacity-limited 1-exterior/5-interior sample reports
that redistribution rather than claiming an even split. A sample containing
unknown labels cannot claim achieved balance. Classification changes only
construction-time selection; it does not add a BAS eligibility check.

To restore or intentionally configure a real BAS sample, pass
`selected_zone_ids=[...]`. They must be a nonempty subset of the AHU's explicit
mapping. The supplied IDs are used exactly, even if their count differs from
the default rounded sample count; the receipt distinguishes an explicit
selection and reports its actual fraction. Explicit IDs are never silently
rebalanced. Custom positive `weights={...}`
may cover the selected subset or the entire mapped inventory. Foreign zone
IDs in either selection or weight configuration are configuration errors.
The input dictionaries are copied, so a caller cannot change an existing
sampler by mutating the original weights.

Missing selected temperatures raise `MissingSelectedZoneError`, identifying
the AHU and missing selected IDs. The sampler does not select a replacement,
drop that zone, switch to a whole-building value, or change the denominator.
Nonnumeric selected inputs raise `ZoneInputError`. Unselected temperatures
are not needed and do not influence the result.

There is no finite-temperature filter, status imputation, stale-value fallback,
or BAS learning restriction in this sampler. NaN and infinity participate in
ordinary floating-point arithmetic and propagate to the result. The actual
BAS/SDK input adapter owns temperature status and the existing driver's checks.
Configuration validation of positive finite weights and a nonempty explicit
mapping is mathematical input validation, not a new sensor-quality or learning
eligibility policy. No temperature units are converted.

The tests cover ceiling/count behavior, AHU isolation, inventory and process
determinism, balanced and capacity-limited strata, partial/unknown metadata,
explicit mappings, unequal weights, input failures without resampling, and
propagation of nonfinite selected values. These tests establish
the sampling/aggregation contract; they do not establish that a 30% sample
represents the comfort of every zone in an AHU.
