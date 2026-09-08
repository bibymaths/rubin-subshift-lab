"""Cellular-automaton domain model."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product

from rubin_subshifts.cellular_automata.local_rules import elementary_rule
from rubin_subshifts.exceptions import DomainValidationError
from rubin_subshifts.symbolic.alphabet import Alphabet
from rubin_subshifts.symbolic.configurations import PeriodicConfiguration
from rubin_subshifts.symbolic.sliding_block_codes import SlidingBlockCode


@dataclass(frozen=True, slots=True)
class CellularAutomaton:
    """A one-dimensional cellular automaton backed by a sliding block code."""

    code: SlidingBlockCode

    def __post_init__(self) -> None:
        if self.code.input_alphabet != self.code.output_alphabet:
            raise DomainValidationError("a cellular automaton must map an alphabet to itself")

    @property
    def alphabet(self) -> Alphabet:
        """Return the state alphabet."""
        return self.code.input_alphabet

    @property
    def name(self) -> str:
        """Return the local rule's display name."""
        return self.code.name

    def apply(self, config: PeriodicConfiguration) -> PeriodicConfiguration:
        """Perform one synchronous global update."""
        return self.code.apply(config)

    def compose(self, other: CellularAutomaton, name: str | None = None) -> CellularAutomaton:
        """Return ``self ∘ other``."""
        return CellularAutomaton(self.code.compose(other.code, name))

    @classmethod
    def elementary(cls, rule_number: int) -> CellularAutomaton:
        """Construct an elementary binary cellular automaton."""
        return cls(elementary_rule(rule_number))

    @classmethod
    def identity(cls, alphabet: Alphabet) -> CellularAutomaton:
        """Construct the identity cellular automaton."""
        return cls(SlidingBlockCode.identity(alphabet))

    @classmethod
    def left_shift(cls, alphabet: Alphabet) -> CellularAutomaton:
        """Construct the left shift ``F(x)_i = x_(i+1)``."""
        mapping = {tuple(block): block[1] for block in product(alphabet.symbols, repeat=2)}
        return cls(SlidingBlockCode.from_mapping(alphabet, alphabet, 0, 1, mapping, "Left shift"))

    @classmethod
    def right_shift(cls, alphabet: Alphabet) -> CellularAutomaton:
        """Construct the right shift ``F(x)_i = x_(i-1)``."""
        mapping = {tuple(block): block[0] for block in product(alphabet.symbols, repeat=2)}
        return cls(SlidingBlockCode.from_mapping(alphabet, alphabet, 1, 0, mapping, "Right shift"))

    @classmethod
    def constant(cls, alphabet: Alphabet, value: object) -> CellularAutomaton:
        """Construct a radius-zero constant cellular automaton."""
        if value not in alphabet:
            raise DomainValidationError("constant value is not in the alphabet")
        return cls(
            SlidingBlockCode.from_mapping(
                alphabet,
                alphabet,
                0,
                0,
                {(symbol,): value for symbol in alphabet},
                f"Constant {value!r}",
            )
        )
