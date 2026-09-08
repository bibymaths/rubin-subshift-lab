"""Figure-construction and export tests without pixel snapshots."""

from __future__ import annotations

import networkx as nx
import plotly.graph_objects as go
import pytest

from rubin_subshifts.cellular_automata import CellularAutomaton, simulate
from rubin_subshifts.exceptions import ExportError
from rubin_subshifts.groups.permutations import Permutation
from rubin_subshifts.reconstruction.experiments import compare_signatures
from rubin_subshifts.reconstruction.signatures import build_signature
from rubin_subshifts.symbolic import Alphabet, PeriodicConfiguration, Word
from rubin_subshifts.symbolic.sft import OneStepSFT
from rubin_subshifts.symbolic.subshifts import binary_full_shift
from rubin_subshifts.visualization.cellular_automata import basin_size_figure, spacetime_figure
from rubin_subshifts.visualization.export import export_figure
from rubin_subshifts.visualization.groups import element_order_figure, orbit_size_figure
from rubin_subshifts.visualization.reconstruction import discrepancy_figure, signature_heatmap
from rubin_subshifts.visualization.subshifts import counts_figure, transition_graph_figure
from rubin_subshifts.visualization.theme import layout


def test_count_and_transition_figures() -> None:
    count = counts_figure([1, 2, 3], [2, 4, 8], title="Counts")
    assert isinstance(count, go.Figure)
    assert list(count.data[0].y) == [2, 4, 8]
    shift = OneStepSFT.golden_mean()
    graph = transition_graph_figure(shift.transition_graph(), title=shift.name, seed=3)
    assert len(graph.data) == 2
    assert graph.layout.title.text == shift.name
    large = nx.path_graph(251)
    aggregate = transition_graph_figure(large, max_nodes=250)
    assert aggregate.data[0].type == "histogram"


def test_ca_and_group_figures(binary: Alphabet) -> None:
    initial = PeriodicConfiguration(Word(binary, (0, 0, 1, 0)))
    history = simulate(CellularAutomaton.elementary(110), initial, 5)
    spacetime = spacetime_figure(history)
    assert spacetime.data[0].type == "heatmap"
    assert len(spacetime.data[0].z) == 6
    with pytest.raises(ValueError, match="empty"):
        spacetime_figure(())
    basin = basin_size_figure((10, 3))
    assert tuple(basin.data[0].y) == (10, 3)
    orbit = orbit_size_figure(((0, 1), (2, 3), (4,)))
    assert tuple(orbit.data[0].x) == (1, 2)
    orders = element_order_figure((Permutation.identity(3), Permutation((1, 2, 0))))
    assert tuple(orders.data[0].x) == (1, 3)


def test_reconstruction_figures() -> None:
    periods = (1, 2, 3, 4)
    full = build_signature(binary_full_shift(), periods, timestamp="x")
    golden = build_signature(OneStepSFT.golden_mean(), periods, timestamp="x")
    heatmap = signature_heatmap((full, golden))
    assert heatmap.data[0].type == "heatmap"
    assert len(heatmap.data[0].y) == 4
    with pytest.raises(ValueError, match="at least one"):
        signature_heatmap(())
    discrepancy = discrepancy_figure(compare_signatures(full, golden))
    assert discrepancy.data[0].type == "bar"


def test_theme_and_export(monkeypatch: pytest.MonkeyPatch) -> None:
    figure = counts_figure([1], [2], title="Counts")
    html = export_figure(figure, "html")
    assert b"<html>" in html
    assert layout("Title", "x", "y")["title"]["text"] == "Title"
    with pytest.raises(ExportError, match="unsupported"):
        export_figure(figure, "jpeg")

    def fail_image(*args: object, **kwargs: object) -> bytes:
        raise RuntimeError("no browser")

    monkeypatch.setattr(figure, "to_image", fail_image)
    with pytest.raises(ExportError, match="Kaleido"):
        export_figure(figure, "png")

    monkeypatch.setattr(figure, "to_image", lambda **_: b"image")
    assert export_figure(figure, "svg") == b"image"
