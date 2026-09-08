"""Full shifts and finite forbidden-word subshifts."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from typing import Protocol

from rubin_subshifts.symbolic.alphabet import Alphabet
from rubin_subshifts.symbolic.configurations import (
    PeriodicConfiguration,
    enumerate_periodic_configurations,
)
from rubin_subshifts.symbolic.languages import ForbiddenLanguage
from rubin_subshifts.symbolic.words import Word, enumerate_words


class FiniteSubshift(Protocol):
    """Protocol for the finite computational interface of a subshift."""

    @property
    def alphabet(self) -> Alphabet:
        """Return the underlying finite alphabet."""
        ...

    @property
    def name(self) -> str:
        """Return the system's display name."""
        ...

    def is_admissible(self, word: Word) -> bool:
        """Return whether a finite word is admissible."""
        ...

    def is_periodic_admissible(self, config: PeriodicConfiguration) -> bool:
        """Return whether a periodic quotient point is admissible."""
        ...

    def periodic_points(
        self, period: int, limit: int | None = None
    ) -> Iterator[PeriodicConfiguration]:
        """Enumerate admissible points on a finite periodic quotient."""
        ...

    def periodic_point_count(self, period: int, limit: int | None = None) -> int:
        """Count admissible points on a finite periodic quotient."""
        ...


@dataclass(frozen=True, slots=True)
class FullShift:
    """The full shift over a finite alphabet."""

    alphabet: Alphabet
    name: str = "Full shift"

    def is_admissible(self, word: Word) -> bool:
        """Return whether the word uses this shift's alphabet."""
        return word.alphabet == self.alphabet

    def is_periodic_admissible(self, config: PeriodicConfiguration) -> bool:
        """Return whether the configuration uses this shift's alphabet."""
        return config.alphabet == self.alphabet

    def words(self, length: int, limit: int | None = None) -> Iterator[Word]:
        """Enumerate all words of the selected length."""
        return enumerate_words(self.alphabet, length, limit)

    def periodic_points(
        self, period: int, limit: int | None = None
    ) -> Iterator[PeriodicConfiguration]:
        """Enumerate all points on the selected periodic quotient."""
        return enumerate_periodic_configurations(self.alphabet, period, limit)

    def periodic_point_count(self, period: int, limit: int | None = None) -> int:
        """Return the number of period-``period`` quotient points."""
        del limit
        return int(len(self.alphabet) ** period)


@dataclass(frozen=True, slots=True)
class ForbiddenWordSubshift:
    """A subshift described by finitely many forbidden words."""

    language: ForbiddenLanguage
    name: str = "Forbidden-word subshift"

    @property
    def alphabet(self) -> Alphabet:
        """Return the underlying alphabet."""
        return self.language.alphabet

    def is_admissible(self, word: Word) -> bool:
        """Test finite-word admissibility."""
        return self.language.is_admissible(word)

    def is_periodic_admissible(self, config: PeriodicConfiguration) -> bool:
        """Test periodic-point admissibility."""
        return self.language.is_periodic_admissible(config)

    def words(self, length: int, limit: int | None = None) -> Iterator[Word]:
        """Enumerate admissible words."""
        return (
            word
            for word in enumerate_words(self.alphabet, length, limit)
            if self.is_admissible(word)
        )

    def periodic_points(
        self, period: int, limit: int | None = None
    ) -> Iterator[PeriodicConfiguration]:
        """Enumerate admissible points of the selected periodic quotient."""
        return (
            config
            for config in enumerate_periodic_configurations(self.alphabet, period, limit)
            if self.is_periodic_admissible(config)
        )

    def periodic_point_count(self, period: int, limit: int | None = None) -> int:
        """Count admissible points by exact bounded enumeration."""
        return sum(1 for _ in self.periodic_points(period, limit))


def binary_full_shift() -> FullShift:
    """Return the canonical binary full shift example."""
    return FullShift(Alphabet((0, 1)), name="Binary full shift")


def golden_mean_shift() -> ForbiddenWordSubshift:
    """Return the binary subshift forbidding consecutive ones."""
    alphabet = Alphabet((0, 1))
    return ForbiddenWordSubshift(
        ForbiddenLanguage(alphabet, (Word(alphabet, (1, 1)),)), name="Golden mean shift"
    )
