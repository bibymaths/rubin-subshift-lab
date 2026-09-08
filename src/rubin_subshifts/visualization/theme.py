"""Centralized accessible Plotly theme."""

from __future__ import annotations

from typing import Any

PALETTE = ("#0F766E", "#2563EB", "#7C3AED", "#EA580C", "#475569", "#DB2777")


def layout(title: str, x_title: str = "", y_title: str = "") -> dict[str, Any]:
    """Return common layout properties for all figures."""
    return {
        "title": {"text": title, "x": 0.02, "xanchor": "left"},
        "font": {"family": "Inter, system-ui, sans-serif", "color": "#132238"},
        "paper_bgcolor": "white",
        "plot_bgcolor": "white",
        "margin": {"l": 55, "r": 25, "t": 65, "b": 50},
        "xaxis": {"title": x_title, "gridcolor": "#E2E8F0", "zeroline": False},
        "yaxis": {"title": y_title, "gridcolor": "#E2E8F0", "zeroline": False},
        "legend": {"orientation": "h", "y": 1.08, "x": 1, "xanchor": "right"},
        "hoverlabel": {"bgcolor": "white"},
    }
