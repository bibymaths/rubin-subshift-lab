"""Home page."""

from __future__ import annotations

import streamlit as st

from rubin_subshifts import __version__
from rubin_subshifts.app.components.explanations import finite_disclaimer
from rubin_subshifts.config import ComputationLimits
from rubin_subshifts.symbolic.sft import OneStepSFT
from rubin_subshifts.visualization.subshifts import counts_figure


def render() -> None:
    """Render project motivation, workflow, guarantees, and safe defaults."""
    st.title("Rubin Subshift Laboratory")
    st.caption(
        "Computational reconstruction of symbolic dynamical systems from "
        "finite automorphism actions"
    )
    finite_disclaimer()
    columns = st.columns(4)
    for column, title, body in zip(
        columns,
        ("Exact finite", "Bounded exhaustive", "Heuristic", "Experimental"),
        (
            "Complete on a declared finite quotient.",
            "Complete only inside an explicit search bound.",
            "Useful evidence without completeness.",
            "A proxy for conjecture formation.",
        ),
        strict=True,
    ):
        column.metric(title, body)
    st.subheader("Research workflow")
    st.markdown(
        "**Subshift** → **cellular automaton** → **finite permutation action** → "
        "**reconstruction signature**"
    )
    sft = OneStepSFT.golden_mean()
    periods = list(range(1, 11))
    st.plotly_chart(
        counts_figure(
            periods,
            [sft.periodic_point_count(period) for period in periods],
            title="Golden mean periodic points",
            x_title="Period",
            y_title="Fixed points",
        ),
        width="stretch",
    )
    limits = ComputationLimits()
    with st.expander("Default computational limits"):
        st.json(limits.model_dump())
    st.caption(f"Rubin Subshift Laboratory {__version__}")
