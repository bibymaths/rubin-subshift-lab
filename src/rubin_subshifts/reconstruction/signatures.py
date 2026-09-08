"""Reproducible finite reconstruction signatures."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Any

from rubin_subshifts import __version__
from rubin_subshifts.config import AlgorithmicGuarantee
from rubin_subshifts.exceptions import DomainValidationError
from rubin_subshifts.symbolic.subshifts import FiniteSubshift, ForbiddenWordSubshift

FeatureTable = tuple[tuple[str, tuple[float, ...]], ...]


@dataclass(frozen=True, slots=True)
class ReconstructionSignature:
    """Metadata-rich collection of explicitly finite invariants."""

    system_name: str
    alphabet: tuple[str, ...]
    subshift_description: str
    generators: tuple[str, ...]
    periods: tuple[int, ...]
    features: FeatureTable
    limits: tuple[tuple[str, int], ...]
    software_version: str
    guarantee: AlgorithmicGuarantee
    random_seed: int
    created_at: str
    completed: bool
    truncated: bool

    def feature(self, name: str) -> tuple[float, ...]:
        """Return one named invariant vector."""
        try:
            return dict(self.features)[name]
        except KeyError as exc:
            raise DomainValidationError(f"signature has no feature named {name!r}") from exc

    def to_json(self) -> dict[str, Any]:
        """Return a JSON-compatible representation."""
        value = asdict(self)
        value["guarantee"] = self.guarantee.value
        return value


def build_signature(
    subshift: FiniteSubshift,
    periods: tuple[int, ...],
    *,
    generators: tuple[str, ...] = (),
    random_seed: int = 0,
    max_configurations: int = 1_000_000,
    timestamp: str | None = None,
) -> ReconstructionSignature:
    """Compute exact periodic-count features within selected finite bounds."""
    if not periods or any(period <= 0 for period in periods):
        raise DomainValidationError("signature periods must be positive")
    fixed_counts: list[int] = []
    truncated = False
    for period in periods:
        estimate = len(subshift.alphabet) ** period
        if isinstance(subshift, ForbiddenWordSubshift) and estimate > max_configurations:
            truncated = True
            count = -1
        else:
            count = subshift.periodic_point_count(period, max_configurations)
        fixed_counts.append(count)
    least_counts = [
        _least_period_count(period, dict(zip(periods, fixed_counts, strict=True)))
        if fixed_counts[index] >= 0
        else -1
        for index, period in enumerate(periods)
    ]
    features: FeatureTable = (
        ("periodic_point_count", tuple(float(value) for value in fixed_counts)),
        ("least_period_count", tuple(float(value) for value in least_counts)),
    )
    return ReconstructionSignature(
        system_name=subshift.name,
        alphabet=tuple(map(str, subshift.alphabet.symbols)),
        subshift_description=type(subshift).__name__,
        generators=generators,
        periods=periods,
        features=features,
        limits=(("max_configurations", max_configurations),),
        software_version=__version__,
        guarantee=AlgorithmicGuarantee.EXACT_FINITE,
        random_seed=random_seed,
        created_at=timestamp or datetime.now(UTC).isoformat(),
        completed=not truncated,
        truncated=truncated,
    )


def _least_period_count(period: int, fixed: dict[int, int]) -> int:
    """Use divisor subtraction when all required fixed counts are available."""
    if period not in fixed:
        return -1
    proper_divisors = [divisor for divisor in range(1, period) if period % divisor == 0]
    if any(divisor not in fixed or fixed[divisor] < 0 for divisor in proper_divisors):
        return -1
    return fixed[period] - sum(_least_period_count(divisor, fixed) for divisor in proper_divisors)
