"""Deterministic graph layouts."""

from __future__ import annotations

from collections.abc import Hashable
from typing import Any

import networkx as nx
import numpy as np


def deterministic_layout(
    graph: nx.Graph[Any, Any, Any], seed: int = 0
) -> dict[Hashable, tuple[float, float]]:
    """Return a seeded spring layout as plain float tuples."""
    positions = nx.spring_layout(graph, seed=seed)
    return {
        node: (float(np.asarray(point)[0]), float(np.asarray(point)[1]))
        for node, point in positions.items()
    }
