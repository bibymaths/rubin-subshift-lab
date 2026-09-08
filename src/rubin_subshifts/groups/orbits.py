"""Orbit and stabilizer computations for explicit finite actions."""

from __future__ import annotations

from rubin_subshifts.exceptions import DomainValidationError
from rubin_subshifts.groups.permutations import Permutation


def orbits(elements: tuple[Permutation, ...]) -> tuple[tuple[int, ...], ...]:
    """Return point orbits under an explicitly enumerated action."""
    if not elements:
        raise DomainValidationError("at least one group element is required")
    size = len(elements[0])
    if any(len(element) != size for element in elements):
        raise DomainValidationError("group elements act on different set sizes")
    unseen = set(range(size))
    result: list[tuple[int, ...]] = []
    while unseen:
        seed = min(unseen)
        orbit = tuple(sorted({element(seed) for element in elements}))
        result.append(orbit)
        unseen.difference_update(orbit)
    return tuple(result)


def stabilizer(elements: tuple[Permutation, ...], point: int) -> tuple[Permutation, ...]:
    """Return the elements fixing ``point``."""
    if not elements:
        raise DomainValidationError("at least one group element is required")
    if point < 0 or point >= len(elements[0]):
        raise DomainValidationError("point lies outside the action domain")
    return tuple(element for element in elements if element(point) == point)
