"""Synchronous cellular-automaton simulation."""

from __future__ import annotations

from rubin_subshifts.cellular_automata.automata import CellularAutomaton
from rubin_subshifts.exceptions import DomainValidationError
from rubin_subshifts.symbolic.configurations import PeriodicConfiguration


def simulate(
    automaton: CellularAutomaton, initial: PeriodicConfiguration, steps: int
) -> tuple[PeriodicConfiguration, ...]:
    """Return the initial state followed by ``steps`` synchronous updates."""
    if steps < 0:
        raise DomainValidationError("number of steps must be non-negative")
    history = [initial]
    for _ in range(steps):
        history.append(automaton.apply(history[-1]))
    return tuple(history)
