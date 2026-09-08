"""Sliding block codes on finite periodic configurations."""

from __future__ import annotations

from collections.abc import Hashable, Mapping
from dataclasses import dataclass
from itertools import product
from typing import Any

from rubin_subshifts.exceptions import DomainValidationError
from rubin_subshifts.symbolic.alphabet import Alphabet
from rubin_subshifts.symbolic.configurations import PeriodicConfiguration
from rubin_subshifts.symbolic.words import Word

RuleTable = tuple[tuple[tuple[Hashable, ...], Hashable], ...]


@dataclass(frozen=True, slots=True)
class SlidingBlockCode:
    """A total local map with declared memory and anticipation."""

    input_alphabet: Alphabet
    output_alphabet: Alphabet
    memory: int
    anticipation: int
    rule_table: RuleTable
    name: str = "Sliding block code"

    def __post_init__(self) -> None:
        if self.memory < 0 or self.anticipation < 0:
            raise DomainValidationError("memory and anticipation must be non-negative")
        width = self.memory + self.anticipation + 1
        keys = [key for key, _ in self.rule_table]
        if any(len(key) != width for key in keys):
            raise DomainValidationError("local-rule inputs have the wrong neighbourhood width")
        if len(set(keys)) != len(keys):
            raise DomainValidationError("local-rule inputs must be unique")
        if any(symbol not in self.input_alphabet for key in keys for symbol in key):
            raise DomainValidationError("local-rule input contains an unknown symbol")
        if any(value not in self.output_alphabet for _, value in self.rule_table):
            raise DomainValidationError("local-rule output contains an unknown symbol")
        expected = set(product(self.input_alphabet.symbols, repeat=width))
        if set(keys) != expected:
            missing = len(expected - set(keys))
            raise DomainValidationError(
                f"local-rule table is not total; {missing} entries are missing"
            )

    @classmethod
    def from_mapping(
        cls,
        input_alphabet: Alphabet,
        output_alphabet: Alphabet,
        memory: int,
        anticipation: int,
        mapping: Mapping[tuple[Hashable, ...], Hashable],
        name: str = "Sliding block code",
    ) -> SlidingBlockCode:
        """Build a code from a mapping using lexicographic rule order."""
        ordered_keys = sorted(
            mapping,
            key=lambda key: tuple(input_alphabet.index(symbol) for symbol in key),
        )
        return cls(
            input_alphabet,
            output_alphabet,
            memory,
            anticipation,
            tuple((key, mapping[key]) for key in ordered_keys),
            name,
        )

    @classmethod
    def identity(cls, alphabet: Alphabet) -> SlidingBlockCode:
        """Return the identity radius-zero code."""
        return cls.from_mapping(
            alphabet, alphabet, 0, 0, {(symbol,): symbol for symbol in alphabet}, "Identity"
        )

    @property
    def radius(self) -> int | None:
        """Return the symmetric radius, or ``None`` for an asymmetric code."""
        return self.memory if self.memory == self.anticipation else None

    @property
    def mapping(self) -> dict[tuple[Hashable, ...], Hashable]:
        """Return a mutable lookup copy of the immutable rule table."""
        return dict(self.rule_table)

    def local(self, neighbourhood: tuple[Hashable, ...]) -> Hashable:
        """Apply the local rule to one neighbourhood."""
        try:
            return self.mapping[neighbourhood]
        except KeyError as exc:
            raise DomainValidationError(f"unknown neighbourhood {neighbourhood!r}") from exc

    def apply(self, config: PeriodicConfiguration) -> PeriodicConfiguration:
        """Apply the global map on a finite periodic quotient."""
        if config.alphabet != self.input_alphabet:
            raise DomainValidationError("configuration uses a different input alphabet")
        output = tuple(
            self.local(config.word.cyclic_window(i, self.memory, self.anticipation))
            for i in range(config.period)
        )
        return PeriodicConfiguration(Word(self.output_alphabet, output))

    def compose(self, other: SlidingBlockCode, name: str | None = None) -> SlidingBlockCode:
        """Return ``self ∘ other`` with the exact composed neighbourhood."""
        if other.output_alphabet != self.input_alphabet:
            raise DomainValidationError("sliding block code alphabets do not compose")
        memory = self.memory + other.memory
        anticipation = self.anticipation + other.anticipation
        width = memory + anticipation + 1
        mapping: dict[tuple[Hashable, ...], Hashable] = {}
        other_lookup = other.mapping
        self_lookup = self.mapping
        for source_block in product(other.input_alphabet.symbols, repeat=width):
            intermediate: list[Hashable] = []
            for offset in range(-self.memory, self.anticipation + 1):
                start = memory + offset - other.memory
                stop = start + other.memory + other.anticipation + 1
                intermediate.append(other_lookup[tuple(source_block[start:stop])])
            mapping[tuple(source_block)] = self_lookup[tuple(intermediate)]
        return SlidingBlockCode.from_mapping(
            other.input_alphabet,
            self.output_alphabet,
            memory,
            anticipation,
            mapping,
            name or f"{self.name} after {other.name}",
        )

    def equal_on(self, other: SlidingBlockCode, configs: tuple[PeriodicConfiguration, ...]) -> bool:
        """Test equality on an explicitly declared finite domain."""
        return all(self.apply(config) == other.apply(config) for config in configs)

    def to_json(self) -> dict[str, Any]:
        """Serialize the complete local rule."""
        return {
            "input_alphabet": self.input_alphabet.to_json(),
            "output_alphabet": self.output_alphabet.to_json(),
            "memory": self.memory,
            "anticipation": self.anticipation,
            "name": self.name,
            "rule_table": [[list(key), value] for key, value in self.rule_table],
        }

    @classmethod
    def from_json(cls, value: dict[str, Any]) -> SlidingBlockCode:
        """Restore a serialized local rule."""
        return cls.from_mapping(
            Alphabet.from_json(value["input_alphabet"]),
            Alphabet.from_json(value["output_alphabet"]),
            int(value["memory"]),
            int(value["anticipation"]),
            {tuple(item[0]): item[1] for item in value["rule_table"]},
            str(value.get("name", "Sliding block code")),
        )
