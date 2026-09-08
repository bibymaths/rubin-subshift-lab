"""Exact finite reversibility and bounded inverse search page."""

from __future__ import annotations

import streamlit as st

from rubin_subshifts.app.components.explanations import finite_disclaimer, guarantee_badge
from rubin_subshifts.cellular_automata.automata import CellularAutomaton
from rubin_subshifts.cellular_automata.reversibility import (
    analyze_finite_map,
    bounded_inverse_search,
)
from rubin_subshifts.symbolic.alphabet import Alphabet


def _selected_automaton(name: str) -> CellularAutomaton:
    alphabet = Alphabet((0, 1))
    return {
        "Identity": CellularAutomaton.identity(alphabet),
        "Left shift": CellularAutomaton.left_shift(alphabet),
        "Right shift": CellularAutomaton.right_shift(alphabet),
        "Constant zero": CellularAutomaton.constant(alphabet, 0),
        "Rule 110": CellularAutomaton.elementary(110),
    }[name]


def render() -> None:
    """Render finite bijectivity evidence and bounded inverse candidates."""
    st.title("Reversibility Laboratory")
    finite_disclaimer()
    name = st.sidebar.selectbox(
        "Automaton", ("Identity", "Left shift", "Right shift", "Constant zero", "Rule 110")
    )
    period = st.sidebar.slider("Test period", 1, 12, 6)
    automaton = _selected_automaton(name)
    if st.button("Check finite quotient"):
        result = analyze_finite_map(automaton, period)
        guarantee_badge(result.guarantee)
        st.metric("Bijective on selected finite quotient", "Yes" if result.bijective else "No")
        st.write(
            {
                "states": result.state_count,
                "image_states": result.image_count,
                "collisions": len(result.collisions),
            }
        )
    with st.expander("Bounded inverse search"):
        max_memory = st.slider("Maximum inverse memory", 0, 2, 1)
        max_anticipation = st.slider("Maximum inverse anticipation", 0, 2, 1)
        if st.button("Search for inverse"):
            search_result = bounded_inverse_search(
                automaton,
                max_memory,
                max_anticipation,
                tuple(range(1, min(period, 5) + 1)),
                max_candidates=10_000,
            )
            guarantee_badge(search_result.guarantee)
            st.write(search_result.limitations)
            if search_result.candidate is not None:
                st.success(f"Candidate found: {search_result.candidate.name}")
                st.json(search_result.candidate.to_json())
            else:
                st.info("No candidate was found within the declared search bound.")
