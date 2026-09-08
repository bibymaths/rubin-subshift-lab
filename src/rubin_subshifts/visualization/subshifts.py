"""Plotly figures for subshift languages and transition graphs."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import networkx as nx
import plotly.graph_objects as go

from rubin_subshifts.graphs.layouts import deterministic_layout
from rubin_subshifts.visualization.theme import PALETTE, layout


def counts_figure(
    x: Sequence[int],
    y: Sequence[int],
    *,
    title: str,
    x_title: str = "Length",
    y_title: str = "Count",
) -> go.Figure:
    """Create an interactive exact-count line chart."""
    figure = go.Figure(
        go.Scatter(
            x=list(x),
            y=list(y),
            mode="lines+markers",
            line={"color": PALETTE[0], "width": 3},
            marker={"size": 8, "symbol": "circle"},
            hovertemplate=f"{x_title}: %{{x}}<br>{y_title}: %{{y}}<extra></extra>",
        )
    )
    figure.update_layout(**layout(title, x_title, y_title))
    return figure


def transition_graph_figure(
    graph: nx.Graph[Any, Any, Any],
    *,
    title: str = "Transition graph",
    seed: int = 0,
    max_nodes: int = 250,
) -> go.Figure:
    """Create a deterministic interactive graph or an aggregate fallback."""
    if graph.number_of_nodes() > max_nodes:
        degrees = [degree for _, degree in graph.degree()]
        figure = go.Figure(go.Histogram(x=degrees, marker_color=PALETTE[0]))
        figure.update_layout(
            **layout(f"{title} — degree summary (graph too large)", "Degree", "Nodes")
        )
        return figure
    positions = deterministic_layout(graph, seed)
    edge_x: list[float | None] = []
    edge_y: list[float | None] = []
    for source, target in graph.edges():
        edge_x.extend((positions[source][0], positions[target][0], None))
        edge_y.extend((positions[source][1], positions[target][1], None))
    node_order = sorted(graph.nodes(), key=repr)
    figure = go.Figure()
    figure.add_trace(
        go.Scatter(
            x=edge_x,
            y=edge_y,
            mode="lines",
            line={"color": "#94A3B8", "width": 1.5},
            hoverinfo="skip",
            name="Allowed transition",
        )
    )
    figure.add_trace(
        go.Scatter(
            x=[positions[node][0] for node in node_order],
            y=[positions[node][1] for node in node_order],
            mode="markers+text",
            marker={"size": 22, "color": PALETTE[0], "line": {"color": "white", "width": 2}},
            text=[str(graph.nodes[node].get("symbol", node)) for node in node_order],
            textposition="top center",
            customdata=[repr(node) for node in node_order],
            hovertemplate="State: %{customdata}<extra></extra>",
            name="States",
        )
    )
    graph_layout = layout(title)
    graph_layout["xaxis"].update({"visible": False})
    graph_layout["yaxis"].update({"visible": False})
    figure.update_layout(**graph_layout)
    return figure
