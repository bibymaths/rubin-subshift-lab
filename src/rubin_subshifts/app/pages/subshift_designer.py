"""Interactive subshift design and exact finite enumeration."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from rubin_subshifts.app.components.downloads import figure_downloads
from rubin_subshifts.app.components.explanations import guarantee_badge
from rubin_subshifts.config import AlgorithmicGuarantee
from rubin_subshifts.symbolic.sft import OneStepSFT
from rubin_subshifts.symbolic.subshifts import binary_full_shift
from rubin_subshifts.visualization.subshifts import counts_figure, transition_graph_figure


def render() -> None:
    """Render built-in SFT controls, graphs, exact counts, and exports."""
    st.title("Subshift Designer")
    model_name = st.sidebar.selectbox("Model", ("Golden mean shift", "Binary full shift"))
    max_length = st.sidebar.slider("Maximum word length", 1, 16, 10)
    max_period = st.sidebar.slider("Maximum period", 1, 16, 10)
    guarantee_badge(AlgorithmicGuarantee.EXACT_FINITE)
    model = OneStepSFT.golden_mean() if model_name == "Golden mean shift" else binary_full_shift()
    lengths = list(range(max_length + 1))
    word_counts = [sum(1 for _ in model.words(length, limit=1_000_000)) for length in lengths]
    periods = list(range(1, max_period + 1))
    period_counts = [model.periodic_point_count(period) for period in periods]
    left, right = st.columns(2)
    with left:
        if isinstance(model, OneStepSFT):
            graph_figure = transition_graph_figure(model.transition_graph(), title=model.name)
            st.plotly_chart(graph_figure, width="stretch")
            st.dataframe(pd.DataFrame(model.adjacency), width="stretch")
        else:
            st.info("Every finite word is admissible in the full shift.")
    with right:
        words_figure = counts_figure(
            lengths,
            word_counts,
            title="Admissible words by length",
            x_title="Length",
            y_title="Words",
        )
        st.plotly_chart(words_figure, width="stretch")
        points_figure = counts_figure(
            periods,
            period_counts,
            title="Periodic points by period",
            x_title="Period",
            y_title="Points",
        )
        st.plotly_chart(points_figure, width="stretch")
        figure_downloads(points_figure, "periodic-points")
    table = pd.DataFrame({"period": periods, "periodic_points": period_counts})
    st.download_button(
        "Download counts as CSV", table.to_csv(index=False), "periodic-points.csv", "text/csv"
    )
