"""Property-based invariants for words and periodic configurations."""

from __future__ import annotations

from hypothesis import given
from hypothesis import strategies as st

from rubin_subshifts.symbolic import Alphabet, PeriodicConfiguration, Word

BINARY = Alphabet((0, 1))


@given(st.integers(min_value=0, max_value=8), st.integers(min_value=0, max_value=255))
def test_word_index_round_trip_property(length: int, raw_index: int) -> None:
    count = len(BINARY) ** length
    index = raw_index % count
    word = Word.from_index(BINARY, length, index)
    assert word.to_index() == index


@given(st.lists(st.integers(min_value=0, max_value=1), min_size=1, max_size=16))
def test_canonical_rotation_and_shift_preserve_period(symbols: list[int]) -> None:
    config = PeriodicConfiguration(Word(BINARY, tuple(symbols)))
    assert config.shift_left().period == config.period
    assert config.canonical() in config.orbit()
    assert config.shift_left(config.period) == config
