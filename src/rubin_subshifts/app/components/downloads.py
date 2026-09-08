"""Download controls shared by laboratory pages."""

from __future__ import annotations

import streamlit as st
from plotly.graph_objects import Figure

from rubin_subshifts.visualization.export import export_figure


def figure_downloads(figure: Figure, stem: str) -> None:
    """Render HTML and best-effort static figure download buttons."""
    st.download_button(
        "Download interactive HTML",
        export_figure(figure, "html"),
        file_name=f"{stem}.html",
        mime="text/html",
    )
