"""Validated experiment runner and bundle export."""

from __future__ import annotations

import json
from typing import cast

import streamlit as st

from rubin_subshifts.experiments.models import ExperimentConfig, ExperimentResult
from rubin_subshifts.experiments.runner import run_signature_comparison
from rubin_subshifts.experiments.serialization import result_bundle, result_json


def render() -> None:
    """Render resource review, execution status, logs, and downloads."""
    st.title("Experiment Runner")
    maximum = st.sidebar.slider("Maximum period", 1, 18, 8)
    seed = st.sidebar.number_input("Random seed", value=20260901)
    config = ExperimentConfig(periods=tuple(range(1, maximum + 1)), random_seed=int(seed))
    st.subheader("Configuration review")
    st.json(config.model_dump(mode="json"))
    st.caption(f"Deterministic experiment ID: {config.identifier}")
    if st.button("Run experiment"):
        with st.status("Running finite experiment", expanded=True) as status:
            st.write("Computing periodic-point and least-period signatures…")
            run_result = run_signature_comparison(config)
            status.update(label=run_result.status.value.capitalize(), state="complete")
        st.session_state.last_experiment = run_result
    result = cast(ExperimentResult | None, st.session_state.get("last_experiment"))
    if result is not None:
        st.success(result.summary)
        st.download_button(
            "Download JSON", result_json(result), "experiment.json", "application/json"
        )
        st.download_button(
            "Download ZIP bundle", result_bundle(result), "experiment.zip", "application/zip"
        )
    uploaded = st.file_uploader("Reload a JSON configuration", type="json")
    if uploaded is not None:
        try:
            restored = ExperimentConfig.model_validate(json.load(uploaded))
            st.success(f"Valid configuration: {restored.identifier}")
        except (ValueError, TypeError) as exc:
            st.error(f"Invalid configuration: {exc}")
