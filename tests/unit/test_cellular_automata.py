"""Cellular-automaton simulation and finite reversibility tests."""

from __future__ import annotations

from collections.abc import Hashable

import pytest

from rubin_subshifts.cellular_automata.automata import CellularAutomaton
from rubin_subshifts.cellular_automata.enumeration import enumerate_elementary_rules
from rubin_subshifts.cellular_automata.local_rules import elementary_rule
from rubin_subshifts.cellular_automata.reversibility import (
    analyze_finite_map,
    bounded_inverse_search,
    preimage_histogram,
)
from rubin_subshifts.cellular_automata.simulation import simulate
from rubin_subshifts.config import AlgorithmicGuarantee
from rubin_subshifts.exceptions import ComputationLimitError, DomainValidationError
from rubin_subshifts.symbolic import Alphabet, PeriodicConfiguration, SlidingBlockCode, Word
from rubin_subshifts.symbolic.configurations import enumerate_periodic_configurations


def test_elementary_rule_table_and_bounds(binary: Alphabet) -> None:
    rule = elementary_rule(110)
    expected = {
        (1, 1, 1): 0,
        (1, 1, 0): 1,
        (1, 0, 1): 1,
        (1, 0, 0): 0,
        (0, 1, 1): 1,
        (0, 1, 0): 1,
        (0, 0, 1): 1,
        (0, 0, 0): 0,
    }
    assert rule.mapping == expected
    assert CellularAutomaton.elementary(110).name == "Elementary CA Rule 110"
    with pytest.raises(DomainValidationError, match=r"\[0, 255\]"):
        elementary_rule(-1)
    with pytest.raises(DomainValidationError, match=r"\[0, 255\]"):
        elementary_rule(256)
    assert rule.input_alphabet == binary


def test_automaton_constructors_and_composition(binary: Alphabet) -> None:
    identity = CellularAutomaton.identity(binary)
    left = CellularAutomaton.left_shift(binary)
    right = CellularAutomaton.right_shift(binary)
    constant = CellularAutomaton.constant(binary, 1)
    config = PeriodicConfiguration(Word(binary, (0, 1, 1, 0)))
    assert identity.apply(config) == config
    assert left.apply(config).word.symbols == (1, 1, 0, 0)
    assert right.apply(config).word.symbols == (0, 0, 1, 1)
    assert left.compose(right).apply(config) == config
    assert right.compose(left).apply(config) == config
    assert constant.apply(config).word.symbols == (1, 1, 1, 1)
    assert left.code.radius is None
    domain = tuple(enumerate_periodic_configurations(binary, 4))
    assert left.compose(right).code.equal_on(identity.code, domain)
    with pytest.raises(DomainValidationError, match="constant"):
        CellularAutomaton.constant(binary, 2)
    other = Alphabet(("a", "b"))
    mapping: dict[tuple[Hashable, ...], Hashable] = {(0,): "a", (1,): "b"}
    with pytest.raises(DomainValidationError, match="map an alphabet to itself"):
        CellularAutomaton(SlidingBlockCode.from_mapping(binary, other, 0, 0, mapping))
    with pytest.raises(DomainValidationError, match="do not compose"):
        identity.code.compose(SlidingBlockCode.identity(other))


def test_simulation(binary: Alphabet) -> None:
    initial = PeriodicConfiguration(Word(binary, (0, 1, 0, 1)))
    history = simulate(CellularAutomaton.left_shift(binary), initial, 3)
    assert len(history) == 4
    assert history[2] == initial
    with pytest.raises(DomainValidationError, match="non-negative"):
        simulate(CellularAutomaton.identity(binary), initial, -1)


def test_exact_finite_analysis_regressions(binary: Alphabet) -> None:
    identity = analyze_finite_map(CellularAutomaton.identity(binary), 4)
    assert identity.guarantee is AlgorithmicGuarantee.EXACT_FINITE
    assert identity.bijective and identity.injective and identity.surjective
    assert identity.state_count == identity.image_count == 16
    assert len(identity.attractor_cycles) == 16
    assert not identity.collisions
    assert not identity.garden_of_eden
    constant = analyze_finite_map(CellularAutomaton.constant(binary, 0), 3)
    assert not constant.bijective
    assert constant.image_count == 1
    assert len(constant.garden_of_eden) == 7
    assert constant.collisions
    assert preimage_histogram(constant)[0] == 7
    assert preimage_histogram(constant)[8] == 1
    assert constant.transient_depths == (0, 1, 1, 1, 1, 1, 1, 1)
    rule110 = analyze_finite_map(CellularAutomaton.elementary(110), 8)
    assert rule110.state_count == 256
    assert rule110.image_count == 154
    assert len(rule110.garden_of_eden) == 102
    assert len(rule110.attractor_cycles) == 6
    with pytest.raises(DomainValidationError, match="positive"):
        analyze_finite_map(CellularAutomaton.identity(binary), 0)
    with pytest.raises(ComputationLimitError, match="finite CA analysis"):
        analyze_finite_map(CellularAutomaton.identity(binary), 10, max_configurations=100)


def test_bounded_inverse_search(binary: Alphabet) -> None:
    left = CellularAutomaton.left_shift(binary)
    result = bounded_inverse_search(left, 1, 1, (1, 2, 3, 4), max_candidates=1_000)
    assert result.found
    assert result.candidate is not None
    assert result.complete_within_bound
    assert "finite periodic" in result.limitations
    constant = bounded_inverse_search(
        CellularAutomaton.constant(binary, 0), 0, 0, (1, 2), max_candidates=10
    )
    assert not constant.found
    assert constant.complete_within_bound
    assert constant.tested_candidates == 4
    truncated = bounded_inverse_search(
        CellularAutomaton.constant(binary, 0), 1, 1, (1,), max_candidates=1
    )
    assert not truncated.found
    assert not truncated.complete_within_bound
    with pytest.raises(DomainValidationError, match="non-negative"):
        bounded_inverse_search(left, -1, 0, (1,))
    with pytest.raises(DomainValidationError, match="positive"):
        bounded_inverse_search(left, 0, 0, ())
    with pytest.raises(ComputationLimitError):
        bounded_inverse_search(left, 0, 0, (10,), max_configurations=10)


def test_elementary_enumeration_limit() -> None:
    rules = tuple(enumerate_elementary_rules())
    assert len(rules) == 256
    assert rules[30].name == "Elementary CA Rule 30"
    with pytest.raises(ComputationLimitError, match="256"):
        tuple(enumerate_elementary_rules(255))
