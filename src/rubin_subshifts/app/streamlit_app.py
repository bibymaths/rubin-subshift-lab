"""Application entry point for Rubin Subshift Laboratory."""

from __future__ import annotations

import streamlit as st

from rubin_subshifts.app.navigation import build_navigation
from rubin_subshifts.app.state import initialize_state

st.set_page_config(
    page_title="Rubin Subshift Laboratory",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded",
)
initialize_state()
build_navigation().run()
