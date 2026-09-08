"""Project metadata, reproducibility, and limitations."""

from __future__ import annotations

import platform

import streamlit as st

from rubin_subshifts import __version__
from rubin_subshifts.app.components.explanations import finite_disclaimer


def render() -> None:
    """Render citation, environment, license, and reproducibility details."""
    st.title("About and reproducibility")
    finite_disclaimer()
    st.write(
        {
            "version": __version__,
            "python": platform.python_version(),
            "platform": platform.platform(),
            "license": "MIT",
        }
    )
    st.code("uv sync --all-groups\nuv run streamlit run src/rubin_subshifts/app/streamlit_app.py")
    st.markdown("Repository: `https://github.com/OWNER/rubin-subshift-lab`")
    st.markdown("Citation metadata is provided in `CITATION.cff`.")
