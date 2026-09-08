"""Periodic configurations on finite cyclic quotients."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any

from rubin_subshifts.exceptions import DomainValidationError
from rubin_subshifts.symbolic.alphabet import Alphabet
from rubin_subshifts.symbolic.words import Word, enumerate_words


@dataclass(frozen=True, slots=True)
class PeriodicConfiguration:
    r"""An exact point of :math:`A^{\mathbb{Z}/n\mathbb{Z}}`.

    The stored word has declared quotient period ``n``. Its least period may be
    a proper divisor of ``n``.
    """

    word: Word

    def __post_init__(self) -> None:
        if len(self.word) == 0:
            raise DomainValidationError("a periodic configuration needs positive period")

    @property
    def alphabet(self) -> Alphabet:
        """Return the underlying alphabet."""
        return self.word.alphabet

    @property
    def period(self) -> int:
        """Return the declared cyclic-quotient period."""
        return len(self.word)

    def __getitem__(self, index: int) -> object:
        return self.word.symbols[index % self.period]

    def shift_left(self, amount: int = 1) -> PeriodicConfiguration:
        """Apply the left shift."""
        return PeriodicConfiguration(self.word.cyclic_shift(amount))

    def shift_right(self, amount: int = 1) -> PeriodicConfiguration:
        """Apply the right shift."""
        return self.shift_left(-amount)

    def orbit(self) -> tuple[PeriodicConfiguration, ...]:
        """Return the distinct shift orbit in deterministic order."""
        return tuple(self.shift_left(i) for i in range(self.least_period))

    @property
    def least_period(self) -> int:
        """Return the least positive shift fixing the configuration."""
        symbols = self.word.symbols
        for candidate in range(1, self.period + 1):
            if self.period % candidate == 0 and all(
                symbols[i] == symbols[i % candidate] for i in range(self.period)
            ):
                return candidate
        return self.period

    def canonical(self) -> PeriodicConfiguration:
        """Return the lexicographically least rotation in alphabet order."""

        def key(config: PeriodicConfiguration) -> tuple[int, ...]:
            return tuple(config.alphabet.index(symbol) for symbol in config.word.symbols)

        return min(self.orbit(), key=key)

    def to_json(self) -> dict[str, Any]:
        """Serialize the configuration."""
        return {
            "word": self.word.to_json(),
            "period": self.period,
            "least_period": self.least_period,
        }

    @classmethod
    def from_json(cls, value: dict[str, Any]) -> PeriodicConfiguration:
        """Restore a serialized periodic configuration."""
        return cls(Word.from_json(value["word"]))


def enumerate_periodic_configurations(
    alphabet: Alphabet, period: int, limit: int | None = None
) -> Iterator[PeriodicConfiguration]:
    """Enumerate all points of the selected finite periodic quotient."""
    if period <= 0:
        raise DomainValidationError("period must be positive")
    for word in enumerate_words(alphabet, period, limit=limit):
        yield PeriodicConfiguration(word)
