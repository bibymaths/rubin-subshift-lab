"""Plotly figures for finite permutation groups and actions."""

from __future__ import annotations

from collections import Counter

import plotly.graph_objects as go

from rubin_subshifts.groups.permutations import Permutation
from rubin_subshifts.visualization.theme import PALETTE, layout


def orbit_size_figure(orbits: tuple[tuple[int, ...], ...]) -> go.Figure:
    """Render the distribution of finite orbit sizes."""
    counts = Counter(map(len, orbits))
    sizes = sorted(counts)
    figure = go.Figure(go.Bar(x=sizes, y=[counts[size] for size in sizes], marker_color=PALETTE[2]))
    figure.update_layout(**layout("Orbit-size distribution", "Orbit size", "Number of orbits"))
    return figure


def element_order_figure(elements: tuple[Permutation, ...]) -> go.Figure:
    """Render the element-order distribution of an enumerated group."""
    counts = Counter(element.order for element in elements)
    orders = sorted(counts)
    figure = go.Figure(
        go.Bar(x=orders, y=[counts[order] for order in orders], marker_color=PALETTE[1])
    )
    figure.update_layout(**layout("Element-order distribution", "Element order", "Elements"))
    return figure
