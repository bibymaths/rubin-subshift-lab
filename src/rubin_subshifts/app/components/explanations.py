"""Shared mathematical caveats and guarantee displays."""

from __future__ import annotations

import streamlit as st

from rubin_subshifts.config import AlgorithmicGuarantee


def guarantee_badge(guarantee: AlgorithmicGuarantee) -> None:
    """Display a prominent guarantee label."""
    labels = {
        AlgorithmicGuarantee.EXACT_FINITE: "Exact on the selected finite domain",
        AlgorithmicGuarantee.EXHAUSTIVE_WITHIN_BOUND: "Exhaustive within the declared bound",
        AlgorithmicGuarantee.HEURISTIC: "Heuristic evidence",
        AlgorithmicGuarantee.EXPERIMENTAL: "Experimental finite proxy",
        AlgorithmicGuarantee.PROOF_GRADE: "Proof-grade under documented assumptions",
    }
    st.info(f"**Guarantee:** {labels[guarantee]}")


def finite_disclaimer() -> None:
    """Display the project's central scope disclaimer."""
    st.warning(
        "Finite computations support exploration and counterexample searches; they do not prove "
        "the full infinite-space version of Rubin's theorem."
    )
