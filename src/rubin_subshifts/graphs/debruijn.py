"""de Bruijn and higher-block graphs."""

from __future__ import annotations

from collections.abc import Hashable
from typing import Any

import networkx as nx

from rubin_subshifts.exceptions import DomainValidationError
from rubin_subshifts.symbolic.alphabet import Alphabet
from rubin_subshifts.symbolic.subshifts import FiniteSubshift
from rubin_subshifts.symbolic.words import enumerate_words


def debruijn_graph(
    alphabet: Alphabet, order: int
) -> nx.DiGraph[tuple[Hashable, ...], dict[str, Any], dict[str, Any]]:
    """Build the directed order-``order`` de Bruijn graph."""
    if order < 1:
        raise DomainValidationError("de Bruijn order must be positive")
    graph: nx.DiGraph[tuple[Hashable, ...], dict[str, Any], dict[str, Any]] = nx.DiGraph(
        order=order
    )
    vertices = tuple(word.symbols for word in enumerate_words(alphabet, order - 1))
    graph.add_nodes_from(vertices)
    for word in enumerate_words(alphabet, order):
        graph.add_edge(word.symbols[:-1], word.symbols[1:], symbol=word.symbols[-1])
    return graph


def higher_block_graph(
    subshift: FiniteSubshift, block_length: int, limit: int = 100_000
) -> nx.DiGraph[tuple[Hashable, ...], dict[str, Any], dict[str, Any]]:
    """Build a finite higher-block presentation using admissible words."""
    if block_length < 1:
        raise DomainValidationError("block length must be positive")
    graph: nx.DiGraph[tuple[Hashable, ...], dict[str, Any], dict[str, Any]] = nx.DiGraph(
        block_length=block_length, name=subshift.name
    )
    vertices = tuple(
        word.symbols
        for word in enumerate_words(subshift.alphabet, block_length, limit)
        if subshift.is_admissible(word)
    )
    graph.add_nodes_from(vertices)
    for candidate in enumerate_words(subshift.alphabet, block_length + 1, limit):
        if subshift.is_admissible(candidate):
            graph.add_edge(candidate.symbols[:-1], candidate.symbols[1:])
    return graph
