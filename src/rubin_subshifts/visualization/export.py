"""Interactive and static Plotly export helpers."""

from __future__ import annotations

import plotly.graph_objects as go

from rubin_subshifts.exceptions import ExportError


def export_figure(figure: go.Figure, format_name: str, scale: float = 2.0) -> bytes:
    """Export a Plotly figure to HTML or a Kaleido-supported static format."""
    normalized = format_name.lower().lstrip(".")
    if normalized == "html":
        return str(figure.to_html(include_plotlyjs="cdn", full_html=True)).encode()
    if normalized not in {"png", "svg", "pdf"}:
        raise ExportError(f"unsupported figure format: {format_name!r}")
    try:
        return bytes(figure.to_image(format=normalized, scale=scale))
    except Exception as exc:
        raise ExportError(
            f"static {normalized.upper()} export failed; verify Kaleido's "
            f"runtime dependencies: {exc}"
        ) from exc
