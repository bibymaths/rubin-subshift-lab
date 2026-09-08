"""Plotly figures for finite reconstruction signatures."""

from __future__ import annotations

import numpy as np
import plotly.graph_objects as go

from rubin_subshifts.reconstruction.experiments import SignatureComparison
from rubin_subshifts.reconstruction.signatures import ReconstructionSignature
from rubin_subshifts.visualization.theme import PALETTE, layout


def signature_heatmap(
    signatures: tuple[ReconstructionSignature, ...],
    *,
    title: str = "Finite reconstruction signatures",
) -> go.Figure:
    """Render log-scaled finite invariant vectors for visual comparison."""
    if not signatures:
        raise ValueError("at least one signature is required")
    rows: list[str] = []
    values: list[list[float]] = []
    for signature in signatures:
        for feature, vector in signature.features:
            rows.append(f"{signature.system_name} · {feature}")
            values.append([float(np.log1p(max(value, 0.0))) for value in vector])
    figure = go.Figure(
        go.Heatmap(
            z=values,
            x=list(signatures[0].periods),
            y=rows,
            colorscale="Viridis",
            colorbar={"title": "log(1 + value)"},
            hovertemplate="Period %{x}<br>%{y}<br>log value %{z:.3f}<extra></extra>",
        )
    )
    figure.update_layout(**layout(title, "Period", "Finite invariant"))
    return figure


def discrepancy_figure(comparison: SignatureComparison) -> go.Figure:
    """Render total absolute discrepancy by finite feature."""
    names = [item.name for item in comparison.discrepancies]
    totals = [sum(item.absolute_difference) for item in comparison.discrepancies]
    colors = [PALETTE[3] if total else PALETTE[0] for total in totals]
    figure = go.Figure(go.Bar(x=names, y=totals, marker_color=colors))
    figure.update_layout(
        **layout("Finite invariant discrepancy", "Invariant", "Total absolute difference")
    )
    return figure
