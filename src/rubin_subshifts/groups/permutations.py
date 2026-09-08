"""Immutable permutations of finite indexed sets."""

from __future__ import annotations

from dataclasses import dataclass
from math import lcm

from rubin_subshifts.exceptions import DomainValidationError


@dataclass(frozen=True, slots=True, order=True)
class Permutation:
    """A permutation represented by the tuple of image indices."""

    images: tuple[int, ...]

    def __post_init__(self) -> None:
        if tuple(sorted(self.images)) != tuple(range(len(self.images))):
            raise DomainValidationError("images must be a permutation of range(n)")

    @classmethod
    def identity(cls, size: int) -> Permutation:
        """Return the identity on ``size`` points."""
        if size < 0:
            raise DomainValidationError("permutation size must be non-negative")
        return cls(tuple(range(size)))

    def __len__(self) -> int:
        return len(self.images)

    def __call__(self, point: int) -> int:
        """Apply the permutation to a point index."""
        return self.images[point]

    def compose(self, other: Permutation) -> Permutation:
        """Return ``self ∘ other``."""
        if len(self) != len(other):
            raise DomainValidationError("permutations act on different set sizes")
        return Permutation(tuple(self.images[other.images[i]] for i in range(len(self))))

    def inverse(self) -> Permutation:
        """Return the inverse permutation."""
        images = [0] * len(self)
        for source, target in enumerate(self.images):
            images[target] = source
        return Permutation(tuple(images))

    def cycles(self, include_fixed: bool = False) -> tuple[tuple[int, ...], ...]:
        """Return disjoint cycles with the least point first."""
        seen: set[int] = set()
        cycles: list[tuple[int, ...]] = []
        for start in range(len(self)):
            if start in seen:
                continue
            cycle: list[int] = []
            current = start
            while current not in seen:
                seen.add(current)
                cycle.append(current)
                current = self.images[current]
            if include_fixed or len(cycle) > 1:
                cycles.append(tuple(cycle))
        return tuple(cycles)

    @property
    def parity(self) -> int:
        """Return ``0`` for even and ``1`` for odd."""
        transpositions = sum(len(cycle) - 1 for cycle in self.cycles(include_fixed=True))
        return transpositions % 2

    @property
    def order(self) -> int:
        """Return the group-theoretic order."""
        return lcm(*(len(cycle) for cycle in self.cycles(include_fixed=True))) if self.images else 1

    def to_cycle_notation(self, one_based: bool = True) -> str:
        """Return compact cycle notation suitable for display or GAP."""
        offset = 1 if one_based else 0
        cycles = self.cycles(include_fixed=False)
        if not cycles:
            return "()"
        return "".join(
            "(" + ",".join(str(point + offset) for point in cycle) + ")" for cycle in cycles
        )
