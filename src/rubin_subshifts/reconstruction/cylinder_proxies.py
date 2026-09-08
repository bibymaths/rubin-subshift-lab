"""Finite cylinder-set proxies used in bounded experiments."""

from __future__ import annotations

from dataclasses import dataclass

from rubin_subshifts.symbolic.words import Word


@dataclass(frozen=True, slots=True)
class CylinderProxy:
    """A finite word standing in for its corresponding cylinder set."""

    word: Word
    offset: int = 0

    def contains(self, candidate: Word) -> bool:
        """Test the defining block in a sufficiently long finite word."""
        stop = self.offset + len(self.word)
        return (
            self.offset >= 0
            and stop <= len(candidate)
            and candidate.symbols[self.offset : stop] == self.word.symbols
        )
