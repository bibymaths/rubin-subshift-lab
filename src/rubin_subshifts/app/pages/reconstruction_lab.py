"""Rubin-inspired finite reconstruction comparison page."""

from __future__ import annotations

import streamlit as st

from rubin_subshifts.app.components.explanations import finite_disclaimer, guarantee_badge
from rubin_subshifts.reconstruction.experiments import compare_signatures
from rubin_subshifts.reconstruction.signatures import build_signature
from rubin_subshifts.symbolic.sft import OneStepSFT
from rubin_subshifts.symbolic.subshifts import binary_full_shift
from rubin_subshifts.visualization.reconstruction import discrepancy_figure, signature_heatmap


def render() -> None:
    """Render exact finite signatures and their experimental comparison."""
    st.title("Reconstruction Laboratory")
    finite_disclaimer()
    maximum = st.sidebar.slider("Maximum tested period", 1, 18, 10)
    if st.button("Compute finite signatures"):
        periods = tuple(range(1, maximum + 1))
        left = build_signature(binary_full_shift(), periods)
        right = build_signature(OneStepSFT.golden_mean(), periods)
        comparison = compare_signatures(left, right)
        guarantee_badge(comparison.guarantee)
        if comparison.distinguished_within_bounds:
            st.success(comparison.statement.capitalize())
        else:
            st.info(comparison.statement.capitalize())
        st.plotly_chart(signature_heatmap((left, right)), width="stretch")
        st.plotly_chart(discrepancy_figure(comparison), width="stretch")
        st.write("Separating features", comparison.differing_features)
