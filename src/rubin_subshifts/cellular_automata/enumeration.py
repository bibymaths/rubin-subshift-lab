"""Bounded cellular-automaton enumeration helpers."""

from __future__ import annotations

from collections.abc import Iterator

from rubin_subshifts.cellular_automata.automata import CellularAutomaton
from rubin_subshifts.exceptions import ComputationLimitError


def enumerate_elementary_rules(limit: int = 256) -> Iterator[CellularAutomaton]:
    """Yield elementary binary rules in numeric order."""
    if limit < 256:
        raise ComputationLimitError("elementary-rule enumeration", 256, limit)
    for rule_number in range(256):
        yield CellularAutomaton.elementary(rule_number)
