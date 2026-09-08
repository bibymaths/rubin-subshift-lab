"""Finite forbidden-word languages."""

from __future__ import annotations

from dataclasses import dataclass

from rubin_subshifts.exceptions import DomainValidationError
from rubin_subshifts.symbolic.alphabet import Alphabet
from rubin_subshifts.symbolic.configurations import PeriodicConfiguration
from rubin_subshifts.symbolic.words import Word, enumerate_words


@dataclass(frozen=True, slots=True)
class ForbiddenLanguage:
    """A finite list of forbidden words over one alphabet."""

    alphabet: Alphabet
    forbidden: tuple[Word, ...]

    def __post_init__(self) -> None:
        if any(word.alphabet != self.alphabet for word in self.forbidden):
            raise DomainValidationError("all forbidden words must use the declared alphabet")
        if any(len(word) == 0 for word in self.forbidden):
            raise DomainValidationError("the empty word cannot be forbidden")

    def is_admissible(self, word: Word) -> bool:
        """Test linear finite-word admissibility."""
        if word.alphabet != self.alphabet:
            raise DomainValidationError("word uses a different alphabet")
        return all(not _contains(word.symbols, pattern.symbols) for pattern in self.forbidden)

    def is_periodic_admissible(self, config: PeriodicConfiguration) -> bool:
        """Test all cyclic occurrences in a periodic configuration."""
        if config.alphabet != self.alphabet:
            raise DomainValidationError("configuration uses a different alphabet")
        n = config.period
        return all(
            not any(
                tuple(config[(start + offset) % n] for offset in range(len(pattern)))
                == pattern.symbols
                for start in range(n)
            )
            for pattern in self.forbidden
        )

    def enumerate(self, length: int, limit: int | None = None) -> tuple[Word, ...]:
        """Return all admissible words of a bounded length."""
        return tuple(
            word
            for word in enumerate_words(self.alphabet, length, limit)
            if self.is_admissible(word)
        )


def _contains(sequence: tuple[object, ...], pattern: tuple[object, ...]) -> bool:
    return any(
        sequence[start : start + len(pattern)] == pattern
        for start in range(len(sequence) - len(pattern) + 1)
    )
