"""Unit and regression tests for the symbolic-dynamics core."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from rubin_subshifts.exceptions import ComputationLimitError, DomainValidationError
from rubin_subshifts.graphs.debruijn import debruijn_graph, higher_block_graph
from rubin_subshifts.symbolic import (
    Alphabet,
    ForbiddenLanguage,
    ForbiddenWordSubshift,
    FullShift,
    OneStepSFT,
    PeriodicConfiguration,
    SlidingBlockCode,
    Word,
    enumerate_words,
)
from rubin_subshifts.symbolic.configurations import enumerate_periodic_configurations
from rubin_subshifts.symbolic.subshifts import binary_full_shift, golden_mean_shift


def test_alphabet_validation_and_json() -> None:
    with pytest.raises(DomainValidationError, match="empty"):
        Alphabet(())
    with pytest.raises(DomainValidationError, match="unique"):
        Alphabet((0, 0))
    with pytest.raises(DomainValidationError, match="hashable"):
        Alphabet(([1],))  # type: ignore[arg-type]
    alphabet = Alphabet.from_iterable(symbol for symbol in ("b", "a"))
    assert tuple(alphabet) == ("b", "a")
    assert len(alphabet) == 2
    assert "a" in alphabet
    assert alphabet.index("b") == 0
    assert Alphabet.from_json(alphabet.to_json()) == alphabet
    with pytest.raises(DomainValidationError, match="not in"):
        alphabet.index("x")
    with pytest.raises(DomainValidationError, match="JSON"):
        Alphabet((complex(1, 2),)).to_json()
    with pytest.raises(FrozenInstanceError):
        alphabet.symbols = ("x",)  # type: ignore[misc]


def test_words_operations_and_validation(binary: Alphabet) -> None:
    left = Word(binary, (0, 1))
    right = Word(binary, (1,))
    assert (left + right).symbols == (0, 1, 1)
    assert left.subword(0, 1).symbols == (0,)
    assert left.cyclic_shift(1).symbols == (1, 0)
    assert left.cyclic_shift(4) == left
    assert Word(binary, ()).cyclic_shift() == Word(binary, ())
    assert Word(binary, (0, 1, 1)).cyclic_window(0, 1, 1) == (1, 0, 1)
    assert left[0] == 0
    assert left[:] == (0, 1)
    assert tuple(left) == (0, 1)
    with pytest.raises(DomainValidationError, match="outside"):
        Word(binary, (2,))
    with pytest.raises(DomainValidationError, match="different"):
        _ = left + Word(Alphabet(("0", "1")), ("0",))
    with pytest.raises(DomainValidationError, match="bounds"):
        left.subword(-1, 1)
    with pytest.raises(DomainValidationError, match="empty"):
        Word(binary, ()).cyclic_window(0, 0, 0)
    with pytest.raises(DomainValidationError, match="non-negative"):
        left.cyclic_window(0, -1, 0)


@pytest.mark.parametrize("length", range(6))
def test_word_index_roundtrip(binary: Alphabet, length: int) -> None:
    for index, word in enumerate(enumerate_words(binary, length)):
        assert word.to_index() == index
        assert Word.from_index(binary, length, index) == word
        assert Word.from_json(word.to_json()) == word


def test_word_enumeration_errors(binary: Alphabet) -> None:
    with pytest.raises(DomainValidationError, match="non-negative"):
        tuple(enumerate_words(binary, -1))
    with pytest.raises(ComputationLimitError, match="requires 8"):
        tuple(enumerate_words(binary, 3, limit=7))
    with pytest.raises(DomainValidationError, match="non-negative"):
        Word.from_index(binary, -1, 0)
    with pytest.raises(DomainValidationError, match="index"):
        Word.from_index(binary, 2, 4)


def test_periodic_configuration_semantics(binary: Alphabet) -> None:
    config = PeriodicConfiguration(Word(binary, (1, 0, 1, 0)))
    assert config.period == 4
    assert config.least_period == 2
    assert config[5] == 0
    assert config[-1] == 0
    assert config.shift_left().word.symbols == (0, 1, 0, 1)
    assert config.shift_right().word.symbols == (0, 1, 0, 1)
    assert len(config.orbit()) == 2
    assert config.canonical().word.symbols == (0, 1, 0, 1)
    assert PeriodicConfiguration.from_json(config.to_json()) == config
    with pytest.raises(DomainValidationError, match="positive period"):
        PeriodicConfiguration(Word(binary, ()))
    with pytest.raises(DomainValidationError, match="positive"):
        tuple(enumerate_periodic_configurations(binary, 0))


def test_forbidden_language_linear_and_cyclic(binary: Alphabet) -> None:
    forbidden = ForbiddenLanguage(binary, (Word(binary, (1, 1)),))
    assert forbidden.is_admissible(Word(binary, (1, 0, 1)))
    assert not forbidden.is_admissible(Word(binary, (0, 1, 1, 0)))
    assert len(forbidden.enumerate(4)) == 8
    assert forbidden.is_periodic_admissible(PeriodicConfiguration(Word(binary, (0, 1))))
    assert not forbidden.is_periodic_admissible(PeriodicConfiguration(Word(binary, (1,))))
    with pytest.raises(DomainValidationError, match="declared alphabet"):
        ForbiddenLanguage(binary, (Word(Alphabet(("a",)), ("a",)),))
    with pytest.raises(DomainValidationError, match="empty"):
        ForbiddenLanguage(binary, (Word(binary, ()),))
    with pytest.raises(DomainValidationError, match="different"):
        forbidden.is_admissible(Word(Alphabet(("a",)), ("a",)))
    with pytest.raises(DomainValidationError, match="different"):
        forbidden.is_periodic_admissible(PeriodicConfiguration(Word(Alphabet(("a",)), ("a",))))


def test_full_and_forbidden_subshifts(binary: Alphabet) -> None:
    full = FullShift(binary)
    assert full.is_admissible(Word(binary, (0, 1)))
    assert not full.is_admissible(Word(Alphabet(("a",)), ("a",)))
    assert full.periodic_point_count(4) == 16
    assert len(tuple(full.words(3))) == 8
    assert len(tuple(full.periodic_points(3))) == 8
    golden = golden_mean_shift()
    assert isinstance(golden, ForbiddenWordSubshift)
    assert golden.periodic_point_count(1) == 1
    assert golden.periodic_point_count(2) == 3
    assert len(tuple(golden.words(4))) == 8
    assert binary_full_shift().name == "Binary full shift"


def test_one_step_sft_counts_and_graph(binary: Alphabet) -> None:
    shift = OneStepSFT.golden_mean()
    assert [shift.periodic_point_count(period) for period in range(1, 6)] == [1, 3, 4, 7, 11]
    assert shift.is_admissible(Word(binary, (1, 0, 1)))
    assert not shift.is_admissible(Word(binary, (1, 1)))
    assert shift.is_periodic_admissible(PeriodicConfiguration(Word(binary, (0, 1))))
    assert not shift.is_periodic_admissible(PeriodicConfiguration(Word(binary, (1,))))
    assert len(tuple(shift.words(5))) == 13
    assert len(tuple(shift.periodic_points(4))) == 7
    graph = shift.transition_graph()
    assert set(graph.edges()) == {(0, 0), (0, 1), (1, 0)}
    assert graph.nodes[1]["symbol"] == "1"
    with pytest.raises(DomainValidationError, match="square"):
        OneStepSFT(binary, ((1,),))
    with pytest.raises(DomainValidationError, match="zero or one"):
        OneStepSFT(binary, ((1, 2), (1, 0)))
    with pytest.raises(DomainValidationError, match="different alphabet"):
        shift.is_admissible(Word(Alphabet(("a",)), ("a",)))
    with pytest.raises(DomainValidationError, match="different alphabet"):
        shift.is_periodic_admissible(PeriodicConfiguration(Word(Alphabet(("a",)), ("a",))))
    with pytest.raises(DomainValidationError, match="positive"):
        shift.periodic_point_count(0)
    assert OneStepSFT.from_matrix(binary, [[1, 1], [1, 0]], "Golden mean shift") == shift


def test_debruijn_and_higher_block_graphs(binary: Alphabet) -> None:
    graph = debruijn_graph(binary, 2)
    assert graph.number_of_nodes() == 2
    assert graph.number_of_edges() == 4
    block = higher_block_graph(OneStepSFT.golden_mean(), 2)
    assert set(block.nodes()) == {(0, 0), (0, 1), (1, 0)}
    with pytest.raises(DomainValidationError, match="positive"):
        debruijn_graph(binary, 0)
    with pytest.raises(DomainValidationError, match="positive"):
        higher_block_graph(OneStepSFT.golden_mean(), 0)


def test_sliding_block_code_validation_and_serialization(binary: Alphabet) -> None:
    identity = SlidingBlockCode.identity(binary)
    assert identity.radius == 0
    assert identity.local((1,)) == 1
    assert SlidingBlockCode.from_json(identity.to_json()) == identity
    with pytest.raises(DomainValidationError, match="non-negative"):
        SlidingBlockCode(binary, binary, -1, 0, (), "bad")
    with pytest.raises(DomainValidationError, match="wrong"):
        SlidingBlockCode(binary, binary, 0, 0, (((0, 1), 0),), "bad")
    with pytest.raises(DomainValidationError, match="unique"):
        SlidingBlockCode(binary, binary, 0, 0, (((0,), 0), ((0,), 1)), "bad")
    with pytest.raises(DomainValidationError, match="unknown symbol"):
        SlidingBlockCode(binary, binary, 0, 0, (((0,), 0), ((2,), 1)), "bad")
    with pytest.raises(DomainValidationError, match="output"):
        SlidingBlockCode(binary, binary, 0, 0, (((0,), 0), ((1,), 2)), "bad")
    with pytest.raises(DomainValidationError, match="not total"):
        SlidingBlockCode(binary, binary, 0, 0, (((0,), 0),), "bad")
    with pytest.raises(DomainValidationError, match="unknown neighbourhood"):
        identity.local((0, 1))
