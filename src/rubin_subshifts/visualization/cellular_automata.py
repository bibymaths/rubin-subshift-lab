"""Plotly figures for cellular-automaton histories and finite maps."""

from __future__ import annotations

import plotly.graph_objects as go

from rubin_subshifts.symbolic.configurations import PeriodicConfiguration
from rubin_subshifts.visualization.theme import layout


def spacetime_figure(
    history: tuple[PeriodicConfiguration, ...], *, title: str = "Cellular-automaton spacetime"
) -> go.Figure:
    """Render a periodic simulation history as an interactive heatmap."""
    if not history:
        raise ValueError("history cannot be empty")
    alphabet = history[0].alphabet
    z = [[alphabet.index(symbol) for symbol in state.word.symbols] for state in history]
    figure = go.Figure(
        go.Heatmap(
            z=z,
            colorscale=[[0, "#08131F"], [1, "#14B8A6"]],
            showscale=False,
            hovertemplate="Time %{y}<br>Cell %{x}<br>State %{z}<extra></extra>",
        )
    )
    figure.update_layout(**layout(title, "Cell index", "Time step"))
    figure.update_yaxes(autorange="reversed")
    return figure


def basin_size_figure(sizes: tuple[int, ...]) -> go.Figure:
    """Render finite attractor basin sizes."""
    figure = go.Figure(go.Bar(x=list(range(1, len(sizes) + 1)), y=sizes, marker_color="#7C3AED"))
    figure.update_layout(**layout("Finite basin sizes", "Attractor", "States in basin"))
    return figure
