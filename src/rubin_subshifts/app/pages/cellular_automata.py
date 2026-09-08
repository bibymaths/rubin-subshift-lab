"""Elementary cellular-automaton simulation and finite action exploration."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from rubin_subshifts.app.components.explanations import guarantee_badge
from rubin_subshifts.cellular_automata.automata import CellularAutomaton
from rubin_subshifts.cellular_automata.reversibility import analyze_finite_map
from rubin_subshifts.cellular_automata.simulation import simulate
from rubin_subshifts.symbolic.configurations import PeriodicConfiguration
from rubin_subshifts.symbolic.words import Word
from rubin_subshifts.visualization.cellular_automata import spacetime_figure


def render() -> None:
    """Render simulation, local rule, and optional finite-map analysis."""
    st.title("Cellular Automata Explorer")
    rule = st.sidebar.number_input("Elementary rule", 0, 255, 110)
    period = st.sidebar.slider("Periodic domain size", 3, 16, 8)
    steps = st.sidebar.slider("Time steps", 1, 128, 32)
    automaton = CellularAutomaton.elementary(int(rule))
    alphabet = automaton.alphabet
    default = tuple(1 if index == period // 2 else 0 for index in range(period))
    initial_text = st.sidebar.text_input("Initial binary state", "".join(map(str, default)))
    if len(initial_text) != period or set(initial_text) - {"0", "1"}:
        st.error(f"Enter exactly {period} binary digits.")
        return
    initial = PeriodicConfiguration(Word(alphabet, tuple(map(int, initial_text))))
    history = simulate(automaton, initial, steps)
    st.plotly_chart(spacetime_figure(history, title=automaton.name), width="stretch")
    st.subheader("Local rule")
    st.dataframe(
        pd.DataFrame(
            [(*key, value) for key, value in reversed(automaton.code.rule_table)],
            columns=("Left", "Center", "Right", "Output"),
        ),
        width="stretch",
    )
    if st.button("Run exact finite analysis"):
        analysis = analyze_finite_map(automaton, period)
        guarantee_badge(analysis.guarantee)
        columns = st.columns(4)
        columns[0].metric("States", analysis.state_count)
        columns[1].metric("Image states", analysis.image_count)
        columns[2].metric("Garden-of-Eden", len(analysis.garden_of_eden))
        columns[3].metric("Attractor cycles", len(analysis.attractor_cycles))
        st.caption("These exact results describe only the selected finite periodic quotient.")
