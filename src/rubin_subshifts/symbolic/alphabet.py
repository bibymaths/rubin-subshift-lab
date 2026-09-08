"""Finite alphabets with deterministic symbol order."""

from __future__ import annotations

from collections.abc import Hashable, Iterable, Iterator
from dataclasses import dataclass
from typing import Any

from rubin_subshifts.exceptions import DomainValidationError


@dataclass(frozen=True, slots=True)
class Alphabet:
    """A finite ordered alphabet.

    Symbol order is the insertion order supplied at construction. It is used
    consistently for lexicographic enumeration and integer encodings.
    """

    symbols: tuple[Hashable, ...]

    def __post_init__(self) -> None:
        if not self.symbols:
            raise DomainValidationError("an alphabet cannot be empty")
        try:
            unique = set(self.symbols)
        except TypeError as exc:
            raise DomainValidationError("alphabet symbols must be hashable") from exc
        if len(unique) != len(self.symbols):
            raise DomainValidationError("alphabet symbols must be unique")

    @classmethod
    def from_iterable(cls, symbols: Iterable[Hashable]) -> Alphabet:
        """Build an alphabet while preserving the iterable's order."""
        return cls(tuple(symbols))

    def __len__(self) -> int:
        return len(self.symbols)

    def __iter__(self) -> Iterator[Hashable]:
        return iter(self.symbols)

    def __contains__(self, symbol: object) -> bool:
        return symbol in self.symbols

    def index(self, symbol: Hashable) -> int:
        """Return the deterministic index of ``symbol``."""
        try:
            return self.symbols.index(symbol)
        except ValueError as exc:
            raise DomainValidationError(f"symbol {symbol!r} is not in the alphabet") from exc

    def to_json(self) -> list[Any]:
        """Return a JSON-compatible symbol list."""
        values: list[Any] = []
        for symbol in self.symbols:
            if not isinstance(symbol, (str, int, float, bool)) and symbol is not None:
                raise DomainValidationError(f"symbol {symbol!r} is not JSON-compatible")
            values.append(symbol)
        return values

    @classmethod
    def from_json(cls, values: list[Any]) -> Alphabet:
        """Restore an alphabet from a JSON-compatible list."""
        return cls(tuple(values))
