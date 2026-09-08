"""One-step shifts of finite type."""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from itertools import pairwise

import networkx as nx
import numpy as np

from rubin_subshifts.exceptions import DomainValidationError
from rubin_subshifts.symbolic.alphabet import Alphabet
from rubin_subshifts.symbolic.configurations import (
    PeriodicConfiguration,
    enumerate_periodic_configurations,
)
from rubin_subshifts.symbolic.words import Word, enumerate_words


@dataclass(frozen=True, slots=True)
class OneStepSFT:
    """A one-step SFT defined by a zero-one adjacency matrix."""

    alphabet: Alphabet
    adjacency: tuple[tuple[int, ...], ...]
    name: str = "One-step SFT"

    def __post_init__(self) -> None:
        size = len(self.alphabet)
        if len(self.adjacency) != size or any(len(row) != size for row in self.adjacency):
            raise DomainValidationError("adjacency matrix must be square with alphabet size")
        if any(entry not in (0, 1) for row in self.adjacency for entry in row):
            raise DomainValidationError("adjacency entries must be zero or one")

    @classmethod
    def from_matrix(
        cls, alphabet: Alphabet, matrix: Sequence[Sequence[int]], name: str = "One-step SFT"
    ) -> OneStepSFT:
        """Create an SFT from a nested sequence."""
        return cls(alphabet, tuple(tuple(int(value) for value in row) for row in matrix), name)

    @classmethod
    def golden_mean(cls) -> OneStepSFT:
        """Return the canonical golden mean SFT."""
        return cls(Alphabet((0, 1)), ((1, 1), (1, 0)), "Golden mean shift")

    def is_admissible(self, word: Word) -> bool:
        """Test whether every adjacent symbol pair is allowed."""
        if word.alphabet != self.alphabet:
            raise DomainValidationError("word uses a different alphabet")
        indices = [self.alphabet.index(symbol) for symbol in word.symbols]
        return all(self.adjacency[left][right] == 1 for left, right in pairwise(indices))

    def is_periodic_admissible(self, config: PeriodicConfiguration) -> bool:
        """Test adjacency including the cyclic closing edge."""
        if config.alphabet != self.alphabet:
            raise DomainValidationError("configuration uses a different alphabet")
        indices = [self.alphabet.index(symbol) for symbol in config.word.symbols]
        return all(
            self.adjacency[indices[i]][indices[(i + 1) % config.period]] == 1
            for i in range(config.period)
        )

    def words(self, length: int, limit: int | None = None) -> Iterator[Word]:
        """Enumerate admissible finite words."""
        return (
            word
            for word in enumerate_words(self.alphabet, length, limit)
            if self.is_admissible(word)
        )

    def periodic_points(
        self, period: int, limit: int | None = None
    ) -> Iterator[PeriodicConfiguration]:
        """Enumerate admissible periodic quotient points."""
        return (
            config
            for config in enumerate_periodic_configurations(self.alphabet, period, limit)
            if self.is_periodic_admissible(config)
        )

    def periodic_point_count(self, period: int, limit: int | None = None) -> int:
        """Return ``trace(A**period)`` exactly for a positive period."""
        del limit
        if period <= 0:
            raise DomainValidationError("period must be positive")
        matrix = np.asarray(self.adjacency, dtype=object)
        return int(np.trace(np.linalg.matrix_power(matrix, period)))

    def transition_graph(self) -> nx.DiGraph[int, dict[str, object], dict[str, object]]:
        """Build the labelled directed transition graph."""
        graph: nx.DiGraph[int, dict[str, object], dict[str, object]] = nx.DiGraph(name=self.name)
        graph.add_nodes_from(range(len(self.alphabet)))
        nx.set_node_attributes(
            graph,
            {i: {"symbol": str(symbol)} for i, symbol in enumerate(self.alphabet)},
        )
        graph.add_edges_from(
            (source, target)
            for source, row in enumerate(self.adjacency)
            for target, allowed in enumerate(row)
            if allowed
        )
        return graph
