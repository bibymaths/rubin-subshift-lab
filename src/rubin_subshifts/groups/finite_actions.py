"""Finite permutation images induced by cellular automata."""

from __future__ import annotations

from rubin_subshifts.cellular_automata.automata import CellularAutomaton
from rubin_subshifts.exceptions import DomainValidationError
from rubin_subshifts.groups.permutations import Permutation
from rubin_subshifts.symbolic.configurations import PeriodicConfiguration


def induced_permutation(
    automaton: CellularAutomaton, domain: tuple[PeriodicConfiguration, ...]
) -> Permutation:
    """Return the finite permutation induced on a closed explicit domain."""
    if not domain:
        raise DomainValidationError("finite action domain cannot be empty")
    index = {state: position for position, state in enumerate(domain)}
    images: list[int] = []
    for state in domain:
        image = automaton.apply(state)
        if image not in index:
            raise DomainValidationError("the declared finite domain is not invariant")
        images.append(index[image])
    try:
        return Permutation(tuple(images))
    except DomainValidationError as exc:
        raise DomainValidationError("the induced finite map is not bijective") from exc
