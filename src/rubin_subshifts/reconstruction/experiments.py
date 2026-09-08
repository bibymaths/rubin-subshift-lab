"""Structured comparisons of finite reconstruction signatures."""

from __future__ import annotations

from dataclasses import dataclass

from rubin_subshifts.config import AlgorithmicGuarantee
from rubin_subshifts.exceptions import DomainValidationError
from rubin_subshifts.reconstruction.signatures import ReconstructionSignature


@dataclass(frozen=True, slots=True)
class FeatureDiscrepancy:
    """Period-by-period discrepancy for one finite invariant."""

    name: str
    left: tuple[float, ...]
    right: tuple[float, ...]
    absolute_difference: tuple[float, ...]


@dataclass(frozen=True, slots=True)
class SignatureComparison:
    """A conservative comparison that makes no theorem-level claim."""

    left_name: str
    right_name: str
    matching_features: tuple[str, ...]
    differing_features: tuple[str, ...]
    discrepancies: tuple[FeatureDiscrepancy, ...]
    distinguished_within_bounds: bool
    statement: str
    guarantee: AlgorithmicGuarantee = AlgorithmicGuarantee.EXPERIMENTAL


def compare_signatures(
    left: ReconstructionSignature, right: ReconstructionSignature
) -> SignatureComparison:
    """Compare features defined over exactly the same tested periods."""
    if left.periods != right.periods:
        raise DomainValidationError("signatures must use identical period selections")
    left_features = dict(left.features)
    right_features = dict(right.features)
    common = sorted(left_features.keys() & right_features.keys())
    discrepancies = tuple(
        FeatureDiscrepancy(
            name,
            left_features[name],
            right_features[name],
            tuple(
                abs(a - b) for a, b in zip(left_features[name], right_features[name], strict=True)
            ),
        )
        for name in common
    )
    matching = tuple(item.name for item in discrepancies if not any(item.absolute_difference))
    differing = tuple(item.name for item in discrepancies if any(item.absolute_difference))
    distinguished = bool(differing)
    statement = (
        "distinguished by the selected finite invariants"
        if distinguished
        else "not distinguished within the tested bounds"
    )
    return SignatureComparison(
        left.system_name,
        right.system_name,
        matching,
        differing,
        discrepancies,
        distinguished,
        statement,
    )
