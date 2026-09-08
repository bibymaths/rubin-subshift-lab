"""Declarative multipage Streamlit navigation."""

from __future__ import annotations

import streamlit as st
from streamlit.navigation.page import StreamlitPage

from rubin_subshifts.app.pages import (
    about,
    automorphism_groups,
    cellular_automata,
    experiment_runner,
    figure_gallery,
    home,
    reconstruction_lab,
    reversibility,
    subshift_designer,
)


def build_navigation() -> StreamlitPage:
    """Create the application navigation tree."""
    pages = {
        "Start": [
            st.Page(
                home.render,
                title="Home",
                icon="🏠",
                url_path="home",
                default=True,
            )
        ],
        "Laboratories": [
            st.Page(
                subshift_designer.render,
                title="Subshift Designer",
                icon="🔀",
                url_path="subshift-designer",
            ),
            st.Page(
                cellular_automata.render,
                title="Cellular Automata",
                icon="◼️",
                url_path="cellular-automata",
            ),
            st.Page(
                reversibility.render,
                title="Reversibility",
                icon="↔️",
                url_path="reversibility",
            ),
            st.Page(
                automorphism_groups.render,
                title="Automorphism Groups",
                icon="🕸️",
                url_path="automorphism-groups",
            ),
            st.Page(
                reconstruction_lab.render,
                title="Reconstruction",
                icon="🧬",
                url_path="reconstruction",
            ),
            st.Page(
                experiment_runner.render,
                title="Experiment Runner",
                icon="▶️",
                url_path="experiment-runner",
            ),
        ],
        "Reference": [
            st.Page(
                figure_gallery.render,
                title="Figure Gallery",
                icon="📊",
                url_path="figure-gallery",
            ),
            st.Page(about.render, title="About", icon="📘", url_path="about"),
        ],
    }
    return st.navigation(pages)
