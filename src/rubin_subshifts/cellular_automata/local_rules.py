"""Constructors and validators for cellular-automaton local rules."""

from __future__ import annotations

from collections.abc import Hashable

from rubin_subshifts.exceptions import DomainValidationError
from rubin_subshifts.symbolic.alphabet import Alphabet
from rubin_subshifts.symbolic.sliding_block_codes import SlidingBlockCode


def elementary_rule(rule_number: int) -> SlidingBlockCode:
    """Return an elementary binary CA using Wolfram's rule numbering."""
    if rule_number < 0 or rule_number > 255:
        raise DomainValidationError("elementary rule number must lie in [0, 255]")
    alphabet = Alphabet((0, 1))
    mapping: dict[tuple[Hashable, ...], Hashable] = {}
    for value in range(8):
        neighbourhood = ((value >> 2) & 1, (value >> 1) & 1, value & 1)
        mapping[neighbourhood] = (rule_number >> value) & 1
    return SlidingBlockCode.from_mapping(
        alphabet, alphabet, 1, 1, mapping, f"Elementary CA Rule {rule_number}"
    )
