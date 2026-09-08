"""Transition graphs for deterministic finite maps."""

from __future__ import annotations

from collections.abc import Hashable, Mapping
from typing import Any

import networkx as nx


def functional_graph(
    mapping: Mapping[Hashable, Hashable],
) -> nx.DiGraph[Hashable, dict[str, Any], dict[str, Any]]:
    """Return the directed functional graph of a finite mapping."""
    graph: nx.DiGraph[Hashable, dict[str, Any], dict[str, Any]] = nx.DiGraph()
    graph.add_edges_from(mapping.items())
    return graph


def attractor_cycles(
    graph: nx.DiGraph[Hashable, dict[str, Any], dict[str, Any]],
) -> tuple[tuple[Hashable, ...], ...]:
    """Return directed cycles of a functional graph in deterministic order."""
    cycles = [tuple(cycle) for cycle in nx.simple_cycles(graph)]
    return tuple(sorted(cycles, key=lambda cycle: (len(cycle), tuple(map(repr, cycle)))))
