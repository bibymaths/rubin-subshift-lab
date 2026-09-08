"""Finite words and exact lexicographic encodings."""

from __future__ import annotations

from collections.abc import Hashable, Iterator
from dataclasses import dataclass
from itertools import product
from typing import Any

from rubin_subshifts.exceptions import ComputationLimitError, DomainValidationError
from rubin_subshifts.symbolic.alphabet import Alphabet


@dataclass(frozen=True, slots=True)
class Word:
    """A finite word over a declared alphabet."""

    alphabet: Alphabet
    symbols: tuple[Hashable, ...]

    def __post_init__(self) -> None:
        invalid = tuple(symbol for symbol in self.symbols if symbol not in self.alphabet)
        if invalid:
            raise DomainValidationError(f"word contains symbols outside its alphabet: {invalid!r}")

    def __len__(self) -> int:
        return len(self.symbols)

    def __iter__(self) -> Iterator[Hashable]:
        return iter(self.symbols)

    def __getitem__(self, item: int | slice) -> Hashable | tuple[Hashable, ...]:
        return self.symbols[item]

    def __add__(self, other: Word) -> Word:
        if self.alphabet != other.alphabet:
            raise DomainValidationError("cannot concatenate words over different alphabets")
        return Word(self.alphabet, self.symbols + other.symbols)

    def subword(self, start: int, stop: int) -> Word:
        """Return the half-open subword ``[start, stop)``."""
        if start < 0 or stop < start or stop > len(self):
            raise DomainValidationError("invalid subword bounds")
        return Word(self.alphabet, self.symbols[start:stop])

    def cyclic_shift(self, amount: int = 1) -> Word:
        """Rotate the word left by ``amount`` positions."""
        if not self.symbols:
            return self
        offset = amount % len(self)
        return Word(self.alphabet, self.symbols[offset:] + self.symbols[:offset])

    def cyclic_window(self, center: int, memory: int, anticipation: int) -> tuple[Hashable, ...]:
        """Extract a local cyclic window around ``center``."""
        if not self.symbols:
            raise DomainValidationError("cannot take a cyclic window of an empty word")
        if memory < 0 or anticipation < 0:
            raise DomainValidationError("memory and anticipation must be non-negative")
        n = len(self)
        return tuple(self.symbols[i % n] for i in range(center - memory, center + anticipation + 1))

    def to_index(self) -> int:
        """Encode the word as a base-|A| integer."""
        base = len(self.alphabet)
        value = 0
        for symbol in self.symbols:
            value = value * base + self.alphabet.index(symbol)
        return value

    @classmethod
    def from_index(cls, alphabet: Alphabet, length: int, index: int) -> Word:
        """Decode a fixed-length word index."""
        if length < 0:
            raise DomainValidationError("word length must be non-negative")
        count = len(alphabet) ** length
        if index < 0 or index >= count:
            raise DomainValidationError(f"index must lie in [0, {count})")
        digits: list[Hashable] = [alphabet.symbols[0]] * length
        for position in range(length - 1, -1, -1):
            index, digit = divmod(index, len(alphabet))
            digits[position] = alphabet.symbols[digit]
        return cls(alphabet, tuple(digits))

    def to_json(self) -> dict[str, Any]:
        """Serialize the word into JSON-compatible data."""
        alphabet = self.alphabet.to_json()
        for symbol in self.symbols:
            if symbol not in self.alphabet:
                raise DomainValidationError("word/alphabet mismatch")
        return {"alphabet": alphabet, "symbols": list(self.symbols)}

    @classmethod
    def from_json(cls, value: dict[str, Any]) -> Word:
        """Restore a serialized word."""
        return cls(Alphabet.from_json(value["alphabet"]), tuple(value["symbols"]))


def enumerate_words(alphabet: Alphabet, length: int, limit: int | None = None) -> Iterator[Word]:
    """Enumerate words in alphabet-defined lexicographic order."""
    if length < 0:
        raise DomainValidationError("word length must be non-negative")
    count = len(alphabet) ** length
    if limit is not None and count > limit:
        raise ComputationLimitError("word enumeration", count, limit)
    for symbols in product(alphabet.symbols, repeat=length):
        yield Word(alphabet, symbols)
