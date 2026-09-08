"""End-to-end tests for principal Typer commands."""

from __future__ import annotations

import subprocess

import pytest
from typer.testing import CliRunner

from rubin_subshifts.cli import app

runner = CliRunner()


def test_help_version_and_examples() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "symbolic dynamics" in result.stdout
    version = runner.invoke(app, ["--version"])
    assert version.exit_code == 0
    assert version.stdout.strip() == "0.1.0"
    examples = runner.invoke(app, ["examples", "list", "--json"])
    assert examples.exit_code == 0
    assert "binary_full_shift" in examples.stdout
    human = runner.invoke(app, ["examples", "list"])
    assert human.exit_code == 0
    assert "golden_mean_shift" in human.stdout


@pytest.mark.parametrize("model", ["golden-mean", "full"])
def test_subshift_analyze(model: str) -> None:
    result = runner.invoke(
        app, ["subshift", "analyze", "--model", model, "--max-period", "4", "--json"]
    )
    assert result.exit_code == 0
    assert "periodic_point_counts" in result.stdout
    invalid = runner.invoke(app, ["subshift", "analyze", "--model", "missing"])
    assert invalid.exit_code != 0


def test_ca_commands() -> None:
    simulation = runner.invoke(
        app, ["ca", "simulate", "--rule", "110", "--initial", "0001", "--steps", "2", "--json"]
    )
    assert simulation.exit_code == 0
    assert '"history"' in simulation.stdout
    human = runner.invoke(
        app, ["ca", "simulate", "--rule", "30", "--initial", "0001", "--steps", "1"]
    )
    assert human.exit_code == 0
    invalid = runner.invoke(app, ["ca", "simulate", "--initial", "abc"])
    assert invalid.exit_code != 0
    finite = runner.invoke(
        app, ["ca", "finite-reversibility", "--rule", "110", "--period", "4", "--json"]
    )
    assert finite.exit_code == 0
    assert '"guarantee": "exact_finite"' in finite.stdout
    inverse = runner.invoke(
        app,
        [
            "ca",
            "inverse-search",
            "--automaton",
            "left-shift",
            "--max-memory",
            "1",
            "--max-anticipation",
            "0",
            "--json",
        ],
    )
    assert inverse.exit_code == 0
    assert '"found": true' in inverse.stdout.lower()
    bad_inverse = runner.invoke(app, ["ca", "inverse-search", "--automaton", "missing"])
    assert bad_inverse.exit_code != 0


def test_group_reconstruction_and_validate() -> None:
    group = runner.invoke(app, ["group", "explore", "--period", "4", "--json"])
    assert group.exit_code == 0
    assert '"group_order": 4' in group.stdout
    reconstruction = runner.invoke(
        app, ["reconstruction", "compare", "--max-period", "4", "--json"]
    )
    assert reconstruction.exit_code == 0
    assert "distinguished by the selected finite invariants" in reconstruction.stdout
    human = runner.invoke(app, ["reconstruction", "compare", "--max-period", "3"])
    assert human.exit_code == 0
    validated = runner.invoke(app, ["validate"])
    assert validated.exit_code == 0
    assert "passed" in validated.stdout


def test_subprocess_commands(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[list[str]] = []

    def fake_run(command: list[str], check: bool = False) -> subprocess.CompletedProcess[str]:
        calls.append(command)
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(subprocess, "run", fake_run)
    assert runner.invoke(app, ["app"]).exit_code == 0
    assert runner.invoke(app, ["docs", "serve"]).exit_code == 0
    assert runner.invoke(app, ["docs", "build"]).exit_code == 0
    assert any("streamlit" in command for command in calls)
    assert ["zensical", "serve"] in calls
    assert ["zensical", "build", "--clean", "--strict"] in calls
