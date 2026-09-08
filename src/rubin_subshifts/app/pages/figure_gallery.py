"""Deterministic gallery of supported Plotly figure types."""

from __future__ import annotations

import streamlit as st

from rubin_subshifts.cellular_automata.automata import CellularAutomaton
from rubin_subshifts.cellular_automata.simulation import simulate
from rubin_subshifts.symbolic.alphabet import Alphabet
from rubin_subshifts.symbolic.configurations import PeriodicConfiguration
from rubin_subshifts.symbolic.sft import OneStepSFT
from rubin_subshifts.symbolic.words import Word
from rubin_subshifts.visualization.cellular_automata import spacetime_figure
from rubin_subshifts.visualization.subshifts import counts_figure, transition_graph_figure


def render() -> None:
    """Render small deterministic examples with their interpretations."""
    st.title("Figure Gallery")
    sft = OneStepSFT.golden_mean()
    st.subheader("Transition graph")
    st.caption("Edges encode allowed adjacent symbols.")
    st.plotly_chart(
        transition_graph_figure(sft.transition_graph(), title=sft.name), width="stretch"
    )
    st.subheader("Periodic-point growth")
    periods = list(range(1, 11))
    st.plotly_chart(
        counts_figure(
            periods, [sft.periodic_point_count(p) for p in periods], title="Exact finite counts"
        ),
        width="stretch",
    )
    st.subheader("Cellular-automaton spacetime")
    alphabet = Alphabet((0, 1))
    initial = PeriodicConfiguration(Word(alphabet, (0, 0, 0, 1, 0, 0, 0, 0)))
    history = simulate(CellularAutomaton.elementary(110), initial, 24)
    st.plotly_chart(spacetime_figure(history), width="stretch")
