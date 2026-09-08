"""Streamlit page smoke and interaction tests."""

from __future__ import annotations

import pytest
from streamlit.testing.v1 import AppTest

PAGES = (
    "home",
    "subshift_designer",
    "cellular_automata",
    "reversibility",
    "automorphism_groups",
    "reconstruction_lab",
    "experiment_runner",
    "figure_gallery",
    "about",
)


def test_multipage_navigation_renders_without_exception() -> None:
    app = AppTest.from_file("src/rubin_subshifts/app/streamlit_app.py")
    app.run(timeout=20)
    assert not app.exception


def page_app(name: str) -> AppTest:
    """Create a wrapper that preserves the page module's globals."""
    return AppTest.from_string(f"from rubin_subshifts.app.pages.{name} import render\nrender()\n")


@pytest.mark.parametrize("name", PAGES)
def test_page_defaults_render_without_exception(name: str) -> None:
    app = page_app(name)
    app.run(timeout=20)
    assert not app.exception


def test_subshift_and_ca_widgets_update() -> None:
    subshift = page_app("subshift_designer").run(timeout=20)
    subshift.selectbox[0].select("Binary full shift").run(timeout=20)
    assert not subshift.exception
    assert len(subshift.get("plotly_chart")) >= 2
    ca = page_app("cellular_automata").run(timeout=20)
    ca.text_input[0].set_value("bad").run(timeout=20)
    assert len(ca.error) == 1


def test_analysis_buttons_execute_small_defaults() -> None:
    ca = page_app("cellular_automata").run(timeout=20)
    ca.button[0].click().run(timeout=20)
    assert not ca.exception
    assert len(ca.metric) == 4
    reversibility_app = page_app("reversibility").run(timeout=20)
    reversibility_app.button[0].click().run(timeout=20)
    assert not reversibility_app.exception
    group = page_app("automorphism_groups").run(timeout=20)
    group.button[0].click().run(timeout=20)
    assert not group.exception
    reconstruction = page_app("reconstruction_lab").run(timeout=20)
    reconstruction.button[0].click().run(timeout=20)
    assert not reconstruction.exception
    experiment = page_app("experiment_runner").run(timeout=20)
    experiment.button[0].click().run(timeout=20)
    assert not experiment.exception
    assert len(experiment.download_button) == 2
