"""A fixed, explicitly mapped zone sample for one AHU; standard library only.

Sampling chooses which sensors participate. Positive weights determine their
subsequent mean. Neither operation changes BAS learning eligibility or statuses.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
from types import MappingProxyType
from typing import Iterable, Mapping


class ZoneInputError(ValueError):
    """The configured zone input cannot be evaluated as supplied."""


class MissingSelectedZoneError(ZoneInputError):
    """A fixed selected sensor is absent; selection has not been changed."""

    def __init__(self, ahu_id: str, missing_zone_ids: Iterable[str]):
        self.ahu_id = ahu_id
        self.missing_zone_ids = tuple(missing_zone_ids)
        super().__init__(f"AHU {ahu_id!r} is missing selected zone inputs: "
                         + ", ".join(repr(zone_id) for zone_id in self.missing_zone_ids))


def _zone_ids(values: Iterable[str], label: str) -> tuple[str, ...]:
    if isinstance(values, (str, bytes)):
        raise ValueError(f"{label} must be an iterable of explicit zone IDs, not one string")
    ids = tuple(values)
    if not ids:
        raise ValueError(f"{label} cannot be empty")
    if any(not isinstance(zone_id, str) or not zone_id for zone_id in ids):
        raise ValueError(f"{label} must contain nonempty string zone IDs")
    if len(set(ids)) != len(ids):
        raise ValueError(f"{label} contains duplicate zone IDs")
    return tuple(sorted(ids))


class ZoneSampler:
    """Select ``ceil(fraction * mapped_count)`` zones once for one AHU.

    The seed includes the AHU ID and a caller-supplied run seed. Sorting the
    explicit inventory before sampling makes selection independent of input
    order and Python's randomized hash seed. Reuse this instance for the run.
    Explicit exterior/interior labels balance the selected counts as evenly
    as available group capacities permit. Missing labels are never guessed.

    ``weights`` are arbitrary positive numeric weights, defaulting to 1 for
    every selected zone. They are not assumed to be floor area. Explicit
    ``selected_zone_ids`` can restore a saved field configuration; these must
    be a nonempty subset of the supplied mapping but need not match a rounded
    fraction. The receipt exposes the actual selected fraction in that case.
    """

    algorithm = "sha256-seed-balanced-strata-v2"

    def __init__(self, ahu_id: str, mapped_zone_ids: Iterable[str], *,
                 fraction: float = 0.3, seed: int | str = 0,
                 weights: Mapping[str, float] | None = None,
                 selected_zone_ids: Iterable[str] | None = None,
                 zone_types: Mapping[str, str | None] | None = None):
        if not isinstance(ahu_id, str) or not ahu_id:
            raise ValueError("ahu_id must be a nonempty string")
        if not isinstance(seed, (int, str)) or isinstance(seed, bool):
            raise ValueError("seed must be an integer or string")
        fraction = float(fraction)
        if not math.isfinite(fraction) or not 0 < fraction <= 1:
            raise ValueError("fraction must be finite and in (0, 1]")
        mapped = _zone_ids(mapped_zone_ids, "mapped_zone_ids")
        self._ahu_id, self._mapped_zone_ids = ahu_id, mapped
        self._fraction, self._seed = fraction, seed

        labels = dict(zone_types) if zone_types is not None else {}
        outside = sorted(set(labels) - set(mapped))
        if outside:
            raise ValueError(f"AHU {ahu_id!r} classifications contain zones outside its explicit mapping: {outside!r}")
        normalized = {}
        for zone_id in mapped:
            label = labels.get(zone_id)
            label = "unknown" if label is None else str(label).strip().lower()
            if label not in ("exterior", "interior", "unknown"):
                raise ValueError(f"zone type for {zone_id!r} must be exterior, interior, or unknown")
            normalized[zone_id] = label
        self._zone_types = MappingProxyType(normalized)
        groups = {label: tuple(zone_id for zone_id in mapped if normalized[zone_id] == label)
                  for label in ("exterior", "interior", "unknown")}
        self._classification_counts = {label: len(ids) for label, ids in groups.items()}
        self._balance_applied = False
        self._fallback_reason = None

        if selected_zone_ids is None:
            payload = json.dumps([seed, ahu_id], ensure_ascii=False, separators=(",", ":"))
            digest = hashlib.sha256(payload.encode("utf-8")).digest()
            rng = random.Random(int.from_bytes(digest, "big"))
            count = max(1, math.ceil(fraction * len(mapped)))
            if groups["exterior"] and groups["interior"]:
                self._balance_applied = True
                self._selection_method = "balanced_exterior_interior"
                allocation = {"exterior": 0, "interior": 0}
                known_count = len(groups["exterior"]) + len(groups["interior"])
                for _ in range(min(count, known_count)):
                    available = [label for label in allocation if allocation[label] < len(groups[label])]
                    fewest = min(allocation[label] for label in available)
                    tied = [label for label in available if allocation[label] == fewest]
                    allocation[rng.choice(tied)] += 1
                chosen = []
                for label in ("exterior", "interior"):
                    chosen.extend(rng.sample(groups[label], allocation[label]))
                remaining = count - len(chosen)
                if remaining:
                    chosen.extend(rng.sample(groups["unknown"], remaining))
                    self._fallback_reason = "insufficient_known_zones_unknown_fill"
                elif abs(allocation["exterior"] - allocation["interior"]) > 1:
                    self._fallback_reason = "known_group_capacity_redistributed"
                selected = tuple(sorted(chosen))
            else:
                selected = tuple(sorted(rng.sample(mapped, count)))
                self._selection_method = "uniform_mapping_fallback"
                if groups["exterior"]:
                    self._fallback_reason = "only_exterior_classified"
                elif groups["interior"]:
                    self._fallback_reason = "only_interior_classified"
                else:
                    self._fallback_reason = "no_exterior_or_interior_classification"
        else:
            selected = _zone_ids(selected_zone_ids, "selected_zone_ids")
            outside = sorted(set(selected) - set(mapped))
            if outside:
                raise ValueError(f"AHU {ahu_id!r} selection contains zones outside its explicit mapping: {outside!r}")
            self._selection_method = "explicit_selection"
            self._fallback_reason = "explicit_selection_not_rebalanced"

        configured_weights = dict(weights) if weights is not None else {}
        outside = sorted(set(configured_weights) - set(mapped))
        if outside:
            raise ValueError(f"AHU {ahu_id!r} weights contain zones outside its explicit mapping: {outside!r}")
        for zone_id, raw in configured_weights.items():
            try:
                weight = float(raw)
            except (TypeError, ValueError, OverflowError) as exc:
                raise ValueError(f"weight for zone {zone_id!r} must be positive and finite") from exc
            if not math.isfinite(weight) or weight <= 0:
                raise ValueError(f"weight for zone {zone_id!r} must be positive and finite")
            configured_weights[zone_id] = weight

        selected_weights = {zone_id: configured_weights.get(zone_id, 1.0) for zone_id in selected}
        total_weight = sum(selected_weights.values())
        if not math.isfinite(total_weight):
            raise ValueError("the sum of selected weights must be finite")
        self._selected_zone_ids = selected
        self._weights = MappingProxyType(selected_weights)
        self._total_weight = total_weight

    @property
    def ahu_id(self) -> str:
        return self._ahu_id

    @property
    def mapped_zone_ids(self) -> tuple[str, ...]:
        return self._mapped_zone_ids

    @property
    def selected_zone_ids(self) -> tuple[str, ...]:
        return self._selected_zone_ids

    @property
    def weights(self) -> Mapping[str, float]:
        """The selected zones' fixed raw weights, exposed read-only."""
        return self._weights

    @property
    def zone_types(self) -> Mapping[str, str]:
        """Explicit classifications, with missing metadata exposed as unknown."""
        return self._zone_types

    def selection_receipt(self) -> dict:
        """Return a fresh JSON-compatible configuration record for audit or restore."""
        selected_counts = {label: sum(self.zone_types[zone_id] == label for zone_id in self.selected_zone_ids)
                           for label in ("exterior", "interior", "unknown")}
        return {
            "ahu_id": self.ahu_id,
            "selection_method": self._selection_method,
            "algorithm": self.algorithm,
            "seed": self._seed,
            "requested_fraction": self._fraction,
            "actual_fraction": len(self.selected_zone_ids) / len(self.mapped_zone_ids),
            "mapped_zone_count": len(self.mapped_zone_ids),
            "selected_zone_count": len(self.selected_zone_ids),
            "mapped_zone_ids": list(self.mapped_zone_ids),
            "selected_zone_ids": list(self.selected_zone_ids),
            "zone_types": dict(self.zone_types),
            "classification_counts": dict(self._classification_counts),
            "classification_coverage": 1 - self._classification_counts["unknown"] / len(self.mapped_zone_ids),
            "unknown_count": self._classification_counts["unknown"],
            "selected_group_counts": selected_counts,
            "balance_applied": self._balance_applied,
            "balance_achieved": self._balance_applied and selected_counts["unknown"] == 0
                                and abs(selected_counts["exterior"] - selected_counts["interior"]) <= 1,
            "fallback_reason": self._fallback_reason,
            "weights": dict(self.weights),
            "normalized_weights": {zone_id: weight / self._total_weight
                                   for zone_id, weight in self.weights.items()},
        }

    def read(self, temperatures: Mapping[str, float], *, with_receipt: bool = False):
        """Return the fixed sample's weighted mean in the input temperature units.

        A missing selected sensor raises; it is never replaced by another zone.
        Nonfinite sensor values are not screened, dropped, or imputed. Their
        ordinary floating-point arithmetic result propagates to the caller,
        which owns actual BAS status handling and decision eligibility.
        """
        missing = tuple(zone_id for zone_id in self.selected_zone_ids if zone_id not in temperatures)
        if missing:
            raise MissingSelectedZoneError(self.ahu_id, missing)
        weighted_values = []
        for zone_id in self.selected_zone_ids:
            try:
                temperature = float(temperatures[zone_id])
            except (TypeError, ValueError, OverflowError) as exc:
                raise ZoneInputError(f"AHU {self.ahu_id!r} selected zone {zone_id!r} has a nonnumeric temperature") from exc
            weighted_values.append(self.weights[zone_id] * temperature)
        result = sum(weighted_values) / self._total_weight
        return (result, self.selection_receipt()) if with_receipt else result
