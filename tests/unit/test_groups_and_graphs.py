"""Tests for finite permutations, groups, graph helpers, and GAP adapters."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from rubin_subshifts.cellular_automata import CellularAutomaton
from rubin_subshifts.exceptions import DomainValidationError, ExternalToolError
from rubin_subshifts.graphs.layouts import deterministic_layout
from rubin_subshifts.graphs.transition import attractor_cycles, functional_graph
from rubin_subshifts.groups.cayley import cayley_graph
from rubin_subshifts.groups.external import (
    gap_available,
    gap_script,
    run_gap_size,
    run_sage_size,
    sage_available,
    sage_script,
    write_gap_script,
    write_sage_script,
)
from rubin_subshifts.groups.finite_actions import induced_permutation
from rubin_subshifts.groups.generated_groups import generate_group
from rubin_subshifts.groups.orbits import orbits, stabilizer
from rubin_subshifts.groups.permutations import Permutation
from rubin_subshifts.symbolic import Alphabet
from rubin_subshifts.symbolic.configurations import enumerate_periodic_configurations


def test_permutation_operations_and_validation() -> None:
    permutation = Permutation((1, 2, 0, 4, 3))
    assert len(permutation) == 5
    assert permutation(0) == 1
    assert permutation.cycles() == ((0, 1, 2), (3, 4))
    assert permutation.cycles(include_fixed=True) == ((0, 1, 2), (3, 4))
    assert permutation.order == 6
    assert permutation.parity == 1
    assert permutation.inverse().images == (2, 0, 1, 4, 3)
    assert permutation.compose(permutation.inverse()) == Permutation.identity(5)
    assert permutation.to_cycle_notation() == "(1,2,3)(4,5)"
    assert permutation.to_cycle_notation(one_based=False) == "(0,1,2)(3,4)"
    assert Permutation.identity(0).order == 1
    assert Permutation.identity(3).to_cycle_notation() == "()"
    with pytest.raises(DomainValidationError, match="permutation"):
        Permutation((0, 0))
    with pytest.raises(DomainValidationError, match="non-negative"):
        Permutation.identity(-1)
    with pytest.raises(DomainValidationError, match="different"):
        Permutation.identity(2).compose(Permutation.identity(3))


def test_generated_group_closure_orbits_and_stabilizers() -> None:
    cycle = Permutation((1, 2, 0))
    group = generate_group((cycle,))
    assert group.order == 3
    assert not group.truncated
    assert group.words == ((), (0,), (0, 0))
    assert group.discovery_depths == (0, 1, 2)
    assert orbits(group.elements) == ((0, 1, 2),)
    assert len(stabilizer(group.elements, 0)) == 1
    graph = cayley_graph(group)
    assert graph.number_of_nodes() == 3
    assert graph.number_of_edges() == 3
    truncated = generate_group((cycle,), max_elements=2)
    assert truncated.truncated
    assert truncated.order is None
    with pytest.raises(DomainValidationError, match="at least one"):
        generate_group(())
    with pytest.raises(DomainValidationError, match="different"):
        generate_group((Permutation.identity(2), Permutation.identity(3)))
    with pytest.raises(DomainValidationError, match="positive"):
        generate_group((cycle,), 0)
    with pytest.raises(DomainValidationError, match="at least one"):
        orbits(())
    with pytest.raises(DomainValidationError, match="different"):
        orbits((Permutation.identity(2), Permutation.identity(3)))
    with pytest.raises(DomainValidationError, match="at least one"):
        stabilizer((), 0)
    with pytest.raises(DomainValidationError, match="outside"):
        stabilizer(group.elements, 3)


def test_induced_shift_permutation_and_non_bijection(binary: Alphabet) -> None:
    domain = tuple(enumerate_periodic_configurations(binary, 3))
    shift = induced_permutation(CellularAutomaton.left_shift(binary), domain)
    assert shift.order == 3
    assert shift.inverse() == induced_permutation(CellularAutomaton.right_shift(binary), domain)
    with pytest.raises(DomainValidationError, match="empty"):
        induced_permutation(CellularAutomaton.identity(binary), ())
    with pytest.raises(DomainValidationError, match="not bijective"):
        induced_permutation(CellularAutomaton.constant(binary, 0), domain)
    restricted = tuple(state for index, state in enumerate(domain) if index != 1)
    with pytest.raises(DomainValidationError, match="not invariant"):
        induced_permutation(CellularAutomaton.left_shift(binary), restricted)


def test_functional_graph_and_layout_are_deterministic() -> None:
    graph = functional_graph({0: 1, 1: 0, 2: 1})
    assert attractor_cycles(graph) == ((0, 1),)
    assert deterministic_layout(graph, seed=42) == deterministic_layout(graph, seed=42)


def test_gap_export_and_runtime(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    generators = (Permutation((1, 2, 0)),)
    script = gap_script(generators)
    assert "Group([(1,2,3)])" in script
    path = write_gap_script(tmp_path / "group.g", generators)
    assert path.read_text(encoding="utf-8") == script
    with pytest.raises(ExternalToolError, match="empty"):
        gap_script(())
    monkeypatch.setattr("shutil.which", lambda _: None)
    assert not gap_available()
    with pytest.raises(ExternalToolError, match="not installed"):
        run_gap_size(path)

    monkeypatch.setattr("shutil.which", lambda _: "/usr/bin/gap")
    assert gap_available()

    def successful_run(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(args=[], returncode=0, stdout="3\n", stderr="")

    monkeypatch.setattr(subprocess, "run", successful_run)
    assert run_gap_size(path) == 3

    def bad_output(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(args=[], returncode=0, stdout="oops", stderr="")

    monkeypatch.setattr(subprocess, "run", bad_output)
    with pytest.raises(ExternalToolError, match="unexpected"):
        run_gap_size(path)

    def failed_run(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        raise subprocess.TimeoutExpired("gap", 1)

    monkeypatch.setattr(subprocess, "run", failed_run)
    with pytest.raises(ExternalToolError, match="failed"):
        run_gap_size(path)


def test_sage_export_and_runtime(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    generators = (Permutation((1, 2, 0)),)
    script = sage_script(generators)
    assert "PermutationGroup" in script
    path = write_sage_script(tmp_path / "group.sage", generators)
    assert path.read_text(encoding="utf-8") == script
    with pytest.raises(ExternalToolError, match="empty"):
        sage_script(())
    monkeypatch.setattr("shutil.which", lambda _: None)
    assert not sage_available()
    with pytest.raises(ExternalToolError, match="not installed"):
        run_sage_size(path)
    monkeypatch.setattr("shutil.which", lambda _: "/usr/bin/sage")
    assert sage_available()
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess([], 0, stdout="3\n", stderr=""),
    )
    assert run_sage_size(path) == 3
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess([], 0, stdout="bad", stderr=""),
    )
    with pytest.raises(ExternalToolError, match="unexpected"):
        run_sage_size(path)

    def failed_run(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        raise OSError("failed")

    monkeypatch.setattr(subprocess, "run", failed_run)
    with pytest.raises(ExternalToolError, match="failed"):
        run_sage_size(path)
