"""Exact finite-quotient analysis and bounded inverse search."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from itertools import product

from rubin_subshifts.cellular_automata.automata import CellularAutomaton
from rubin_subshifts.config import AlgorithmicGuarantee
from rubin_subshifts.exceptions import ComputationLimitError, DomainValidationError
from rubin_subshifts.symbolic.configurations import (
    PeriodicConfiguration,
    enumerate_periodic_configurations,
)
from rubin_subshifts.symbolic.sliding_block_codes import SlidingBlockCode


@dataclass(frozen=True, slots=True)
class FiniteMapAnalysis:
    """Exact analysis of a CA on one finite periodic quotient."""

    period: int
    state_count: int
    image_count: int
    injective: bool
    surjective: bool
    bijective: bool
    collisions: tuple[
        tuple[PeriodicConfiguration, PeriodicConfiguration, PeriodicConfiguration], ...
    ]
    garden_of_eden: tuple[PeriodicConfiguration, ...]
    preimage_counts: tuple[int, ...]
    attractor_cycles: tuple[tuple[int, ...], ...]
    transient_depths: tuple[int, ...]
    guarantee: AlgorithmicGuarantee = AlgorithmicGuarantee.EXACT_FINITE


@dataclass(frozen=True, slots=True)
class InverseSearchResult:
    """Evidence produced by a bounded exhaustive inverse-rule search."""

    found: bool
    candidate: SlidingBlockCode | None
    tested_candidates: int
    validation_periods: tuple[int, ...]
    complete_within_bound: bool
    limitations: str
    guarantee: AlgorithmicGuarantee = AlgorithmicGuarantee.EXHAUSTIVE_WITHIN_BOUND


def analyze_finite_map(
    automaton: CellularAutomaton, period: int, max_configurations: int = 1_000_000
) -> FiniteMapAnalysis:
    """Exhaustively analyze the induced map on period-``period`` states."""
    if period <= 0:
        raise DomainValidationError("period must be positive")
    estimate = len(automaton.alphabet) ** period
    if estimate > max_configurations:
        raise ComputationLimitError("finite CA analysis", estimate, max_configurations)
    states = tuple(enumerate_periodic_configurations(automaton.alphabet, period))
    index = {state: position for position, state in enumerate(states)}
    images = tuple(automaton.apply(state) for state in states)
    image_indices = tuple(index[image] for image in images)
    preimages: dict[int, list[int]] = defaultdict(list)
    for source, target in enumerate(image_indices):
        preimages[target].append(source)
    collision_examples: list[
        tuple[PeriodicConfiguration, PeriodicConfiguration, PeriodicConfiguration]
    ] = []
    for target in sorted(preimages):
        sources = preimages[target]
        if len(sources) > 1:
            collision_examples.append((states[sources[0]], states[sources[1]], states[target]))
    missing = tuple(
        states[position] for position in range(len(states)) if position not in preimages
    )
    cycles, depths = _functional_graph_structure(image_indices)
    image_count = len(preimages)
    bijective = image_count == len(states)
    return FiniteMapAnalysis(
        period=period,
        state_count=len(states),
        image_count=image_count,
        injective=bijective,
        surjective=bijective,
        bijective=bijective,
        collisions=tuple(collision_examples),
        garden_of_eden=missing,
        preimage_counts=tuple(len(preimages.get(position, ())) for position in range(len(states))),
        attractor_cycles=cycles,
        transient_depths=depths,
    )


def bounded_inverse_search(
    automaton: CellularAutomaton,
    max_memory: int,
    max_anticipation: int,
    validation_periods: tuple[int, ...],
    max_candidates: int = 100_000,
    max_configurations: int = 1_000_000,
) -> InverseSearchResult:
    """Search inverse local maps exhaustively within the declared bounds."""
    if max_memory < 0 or max_anticipation < 0:
        raise DomainValidationError("inverse bounds must be non-negative")
    if not validation_periods or any(period <= 0 for period in validation_periods):
        raise DomainValidationError("validation periods must be positive")
    alphabet = automaton.alphabet
    identity = CellularAutomaton.identity(alphabet)
    domains = {
        period: tuple(
            enumerate_periodic_configurations(
                alphabet,
                period,
                limit=max_configurations,
            )
        )
        for period in validation_periods
    }
    tested = 0
    for memory in range(max_memory + 1):
        for anticipation in range(max_anticipation + 1):
            contexts = tuple(product(alphabet.symbols, repeat=memory + anticipation + 1))
            rule_count = len(alphabet) ** len(contexts)
            for outputs in product(alphabet.symbols, repeat=len(contexts)):
                if tested >= max_candidates:
                    return InverseSearchResult(
                        False,
                        None,
                        tested,
                        validation_periods,
                        False,
                        f"search truncated at {max_candidates:,} candidates before exhausting a "
                        f"rule space containing at least {rule_count:,} rules at the current bound",
                    )
                tested += 1
                code = SlidingBlockCode.from_mapping(
                    alphabet,
                    alphabet,
                    memory,
                    anticipation,
                    dict(zip(contexts, outputs, strict=True)),
                    f"Inverse candidate m={memory}, a={anticipation}",
                )
                candidate = CellularAutomaton(code)
                left = automaton.compose(candidate)
                right = candidate.compose(automaton)
                if all(
                    left.code.equal_on(identity.code, domains[period])
                    and right.code.equal_on(identity.code, domains[period])
                    for period in validation_periods
                ):
                    return InverseSearchResult(
                        True,
                        code,
                        tested,
                        validation_periods,
                        True,
                        "candidate is verified on the declared finite periodic quotients only",
                    )
    return InverseSearchResult(
        False,
        None,
        tested,
        validation_periods,
        True,
        "all inverse rules within the declared memory and anticipation bounds were tested",
    )


def _functional_graph_structure(
    mapping: tuple[int, ...],
) -> tuple[tuple[tuple[int, ...], ...], tuple[int, ...]]:
    cycles: set[tuple[int, ...]] = set()
    depths: list[int] = [0] * len(mapping)
    for start in range(len(mapping)):
        path: list[int] = []
        local: dict[int, int] = {}
        current = start
        while current not in local:
            local[current] = len(path)
            path.append(current)
            current = mapping[current]
        cycle_start = local[current]
        cycle = path[cycle_start:]
        rotations = [tuple(cycle[i:] + cycle[:i]) for i in range(len(cycle))]
        cycles.add(min(rotations))
        for distance, node in enumerate(reversed(path[:cycle_start]), start=1):
            depths[node] = max(depths[node], distance)
    ordered_cycles = tuple(sorted(cycles, key=lambda item: (len(item), item)))
    return ordered_cycles, tuple(depths)


def preimage_histogram(analysis: FiniteMapAnalysis) -> Counter[int]:
    """Return the exact distribution of finite preimage multiplicities."""
    return Counter(analysis.preimage_counts)
