"""Property-based algebraic tests for local maps and permutations."""

from __future__ import annotations

from hypothesis import given
from hypothesis import strategies as st

from rubin_subshifts.cellular_automata import CellularAutomaton
from rubin_subshifts.groups import Permutation
from rubin_subshifts.symbolic import Alphabet, PeriodicConfiguration, Word


@given(st.permutations([0, 1, 2, 3]))
def test_permutation_inverse_identity(images: list[int]) -> None:
    permutation = Permutation(tuple(images))
    identity = Permutation.identity(4)
    assert permutation.compose(permutation.inverse()) == identity
    assert permutation.inverse().compose(permutation) == identity


@given(
    st.permutations([0, 1, 2]),
    st.permutations([0, 1, 2]),
    st.permutations([0, 1, 2]),
)
def test_permutation_associativity(a: list[int], b: list[int], c: list[int]) -> None:
    left = Permutation(tuple(a)).compose(Permutation(tuple(b))).compose(Permutation(tuple(c)))
    right = Permutation(tuple(a)).compose(Permutation(tuple(b)).compose(Permutation(tuple(c))))
    assert left == right


@given(st.lists(st.integers(min_value=0, max_value=1), min_size=1, max_size=10))
def test_identity_and_shift_composition(symbols: list[int]) -> None:
    alphabet = Alphabet((0, 1))
    config = PeriodicConfiguration(Word(alphabet, tuple(symbols)))
    identity = CellularAutomaton.identity(alphabet)
    left = CellularAutomaton.left_shift(alphabet)
    right = CellularAutomaton.right_shift(alphabet)
    assert identity.apply(config) == config
    assert left.compose(right).apply(config) == config
