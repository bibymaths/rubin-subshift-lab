"""Typer command-line interface for all standard laboratory workflows."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Annotated, Any

import typer
from rich.console import Console
from rich.table import Table

from rubin_subshifts import __version__
from rubin_subshifts.cellular_automata.automata import CellularAutomaton
from rubin_subshifts.cellular_automata.reversibility import (
    analyze_finite_map,
    bounded_inverse_search,
)
from rubin_subshifts.cellular_automata.simulation import simulate
from rubin_subshifts.experiments.models import ExperimentConfig
from rubin_subshifts.experiments.runner import run_signature_comparison
from rubin_subshifts.experiments.serialization import result_json
from rubin_subshifts.groups.finite_actions import induced_permutation
from rubin_subshifts.groups.generated_groups import generate_group
from rubin_subshifts.groups.orbits import orbits
from rubin_subshifts.symbolic.alphabet import Alphabet
from rubin_subshifts.symbolic.configurations import (
    PeriodicConfiguration,
    enumerate_periodic_configurations,
)
from rubin_subshifts.symbolic.sft import OneStepSFT
from rubin_subshifts.symbolic.words import Word

console = Console()
app = typer.Typer(
    help="Finite experiments in symbolic dynamics and Rubin-inspired reconstruction.",
    invoke_without_command=True,
)
examples_app = typer.Typer(help="Inspect built-in deterministic examples.")
subshift_app = typer.Typer(help="Analyze full shifts and subshifts of finite type.")
ca_app = typer.Typer(help="Simulate and analyze cellular automata.")
group_app = typer.Typer(help="Explore finite permutation images.")
reconstruction_app = typer.Typer(help="Compare finite reconstruction signatures.")
docs_app = typer.Typer(help="Serve or build the Zensical documentation.")
app.add_typer(examples_app, name="examples")
app.add_typer(subshift_app, name="subshift")
app.add_typer(ca_app, name="ca")
app.add_typer(group_app, name="group")
app.add_typer(reconstruction_app, name="reconstruction")
app.add_typer(docs_app, name="docs")


def _emit(value: dict[str, Any], json_output: bool) -> None:
    if json_output:
        typer.echo(json.dumps(value, indent=2, sort_keys=True))
    else:
        for key, item in value.items():
            console.print(f"[bold]{key.replace('_', ' ').title()}:[/bold] {item}")


@app.callback()
def main(
    version: Annotated[bool, typer.Option("--version", help="Show the package version.")] = False,
) -> None:
    """Run Rubin Subshift Laboratory commands."""
    if version:
        typer.echo(__version__)
        raise typer.Exit()


@examples_app.command("list")
def list_examples(json_output: Annotated[bool, typer.Option("--json")] = False) -> None:
    """List built-in examples."""
    examples = [
        "binary_full_shift",
        "golden_mean_shift",
        "identity_ca",
        "left_shift",
        "right_shift",
        "constant_ca",
        "elementary_ca_110",
    ]
    if json_output:
        typer.echo(json.dumps({"examples": examples}))
    else:
        table = Table("Identifier")
        for example in examples:
            table.add_row(example)
        console.print(table)


@subshift_app.command("analyze")
def analyze_subshift(
    model: Annotated[str, typer.Option(help="golden-mean or full")] = "golden-mean",
    max_period: Annotated[int, typer.Option(min=1, max=24)] = 10,
    json_output: Annotated[bool, typer.Option("--json")] = False,
) -> None:
    """Compute exact periodic-point counts for a built-in shift."""
    if model == "golden-mean":
        subshift = OneStepSFT.golden_mean()
    elif model == "full":
        alphabet = Alphabet((0, 1))
        counts = [len(alphabet) ** period for period in range(1, max_period + 1)]
        _emit({"model": "Binary full shift", "periodic_point_counts": counts}, json_output)
        return
    else:
        raise typer.BadParameter("model must be 'golden-mean' or 'full'")
    counts = [subshift.periodic_point_count(period) for period in range(1, max_period + 1)]
    _emit({"model": subshift.name, "periodic_point_counts": counts}, json_output)


@ca_app.command("simulate")
def simulate_ca(
    rule: Annotated[int, typer.Option(min=0, max=255)] = 110,
    initial: Annotated[str, typer.Option(help="Periodic binary word")] = "00010000",
    steps: Annotated[int, typer.Option(min=0, max=1_000)] = 16,
    json_output: Annotated[bool, typer.Option("--json")] = False,
) -> None:
    """Simulate an elementary CA with periodic boundaries."""
    if not initial or set(initial) - {"0", "1"}:
        raise typer.BadParameter("initial must be a non-empty binary word")
    automaton = CellularAutomaton.elementary(rule)
    config = PeriodicConfiguration(Word(automaton.alphabet, tuple(map(int, initial))))
    history = simulate(automaton, config, steps)
    rows = ["".join(map(str, state.word.symbols)) for state in history]
    if json_output:
        typer.echo(json.dumps({"rule": rule, "history": rows}))
    else:
        console.print("\n".join(rows))


@ca_app.command("finite-reversibility")
def finite_reversibility(
    rule: Annotated[int, typer.Option(min=0, max=255)] = 110,
    period: Annotated[int, typer.Option(min=1, max=20)] = 8,
    json_output: Annotated[bool, typer.Option("--json")] = False,
) -> None:
    """Analyze exact bijectivity on one finite periodic quotient."""
    result = analyze_finite_map(CellularAutomaton.elementary(rule), period)
    _emit(
        {
            "guarantee": result.guarantee.value,
            "period": period,
            "states": result.state_count,
            "image_states": result.image_count,
            "injective": result.injective,
            "surjective": result.surjective,
            "bijective": result.bijective,
            "garden_of_eden": len(result.garden_of_eden),
            "attractor_cycles": len(result.attractor_cycles),
        },
        json_output,
    )


@ca_app.command("inverse-search")
def inverse_search(
    automaton_name: Annotated[str, typer.Option("--automaton")] = "left-shift",
    max_memory: Annotated[int, typer.Option(min=0, max=3)] = 1,
    max_anticipation: Annotated[int, typer.Option(min=0, max=3)] = 1,
    json_output: Annotated[bool, typer.Option("--json")] = False,
) -> None:
    """Search a bounded inverse local-rule space."""
    alphabet = Alphabet((0, 1))
    choices = {
        "identity": CellularAutomaton.identity(alphabet),
        "left-shift": CellularAutomaton.left_shift(alphabet),
        "right-shift": CellularAutomaton.right_shift(alphabet),
        "constant": CellularAutomaton.constant(alphabet, 0),
    }
    if automaton_name not in choices:
        raise typer.BadParameter(f"automaton must be one of {', '.join(choices)}")
    result = bounded_inverse_search(
        choices[automaton_name], max_memory, max_anticipation, (1, 2, 3, 4), max_candidates=100_000
    )
    _emit(
        {
            "found": result.found,
            "tested_candidates": result.tested_candidates,
            "complete_within_bound": result.complete_within_bound,
            "candidate": result.candidate.to_json() if result.candidate else None,
            "limitations": result.limitations,
        },
        json_output,
    )


@group_app.command("explore")
def explore_group(
    period: Annotated[int, typer.Option(min=1, max=16)] = 6,
    cap: Annotated[int, typer.Option(min=1, max=100_000)] = 10_000,
    json_output: Annotated[bool, typer.Option("--json")] = False,
) -> None:
    """Generate the finite image of the shift action."""
    alphabet = Alphabet((0, 1))
    domain = tuple(enumerate_periodic_configurations(alphabet, period))
    generator = induced_permutation(CellularAutomaton.left_shift(alphabet), domain)
    group = generate_group((generator,), cap)
    action_orbits = orbits(group.elements)
    _emit(
        {
            "period": period,
            "domain_size": len(domain),
            "enumerated_group_elements": len(group.elements),
            "group_order": group.order,
            "truncated": group.truncated,
            "orbit_sizes": [len(orbit) for orbit in action_orbits],
        },
        json_output,
    )


@reconstruction_app.command("compare")
def compare_reconstruction(
    max_period: Annotated[int, typer.Option(min=1, max=24)] = 10,
    config_path: Annotated[
        Path | None, typer.Option("--config", exists=True, dir_okay=False)
    ] = None,
    json_output: Annotated[bool, typer.Option("--json")] = False,
) -> None:
    """Compare finite signatures of two built-in subshifts."""
    config = (
        ExperimentConfig.model_validate_json(config_path.read_text(encoding="utf-8"))
        if config_path
        else ExperimentConfig(periods=tuple(range(1, max_period + 1)))
    )
    result = run_signature_comparison(config)
    if json_output:
        typer.echo(result_json(result).decode())
    else:
        _emit(
            {
                "experiment_id": result.identifier,
                "status": result.status.value,
                "result": result.summary,
                "guarantee": result.guarantee.value,
            },
            False,
        )


@app.command("app")
def launch_app() -> None:
    """Launch Streamlit using a documented subprocess command."""
    script = Path(__file__).parent / "app" / "streamlit_app.py"
    completed = subprocess.run([sys.executable, "-m", "streamlit", "run", str(script)], check=False)
    raise typer.Exit(completed.returncode)


@docs_app.command("serve")
def docs_serve() -> None:
    """Serve the Zensical documentation."""
    completed = subprocess.run(["zensical", "serve"], check=False)
    raise typer.Exit(completed.returncode)


@docs_app.command("build")
def docs_build() -> None:
    """Build the Zensical documentation in strict mode."""
    completed = subprocess.run(["zensical", "build", "--clean", "--strict"], check=False)
    raise typer.Exit(completed.returncode)


@app.command("validate")
def validate() -> None:
    """Run fast internal mathematical smoke checks."""
    alphabet = Alphabet((0, 1))
    left = CellularAutomaton.left_shift(alphabet)
    right = CellularAutomaton.right_shift(alphabet)
    domain = tuple(enumerate_periodic_configurations(alphabet, 4))
    if not left.compose(right).code.equal_on(CellularAutomaton.identity(alphabet).code, domain):
        console.print("[red]Shift inverse smoke check failed.[/red]")
        raise typer.Exit(1)
    console.print("[green]Validation passed.[/green]")
