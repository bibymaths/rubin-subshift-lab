"""Cayley graph construction for enumerated finite groups."""

from __future__ import annotations

from typing import Any

import networkx as nx

from rubin_subshifts.groups.generated_groups import GeneratedGroup


def cayley_graph(
    group: GeneratedGroup,
) -> nx.MultiDiGraph[int, dict[str, Any], dict[str, Any]]:
    """Build the right-labelled Cayley graph of enumerated elements."""
    graph: nx.MultiDiGraph[int, dict[str, Any], dict[str, Any]] = nx.MultiDiGraph(
        truncated=group.truncated
    )
    lookup = {element: index for index, element in enumerate(group.elements)}
    graph.add_nodes_from(range(len(group.elements)))
    for source, element in enumerate(group.elements):
        for generator_index, generator in enumerate(group.generators):
            target_element = generator.compose(element)
            if target_element in lookup:
                graph.add_edge(source, lookup[target_element], generator=generator_index)
    return graph
