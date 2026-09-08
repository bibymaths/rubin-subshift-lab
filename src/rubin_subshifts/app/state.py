"""Session-state defaults for the Streamlit application."""

from __future__ import annotations

from typing import Any

import streamlit as st

DEFAULTS: dict[str, Any] = {"random_seed": 20260901, "last_experiment": None}


def initialize_state() -> None:
    """Populate missing deterministic session-state defaults."""
    for key, value in DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = value
