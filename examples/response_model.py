"""Build a finite symbolic ERK-response model from discrete replicate trajectories.

The example deliberately starts after normalization and discretization. It uses
replicate-supported adjacent transitions to construct a one-step shift of finite
type, then summarizes the model with the current reconstruction-signature API.
"""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from itertools import pairwise
from typing import Any

from rubin_subshifts.reconstruction import build_signature
from rubin_subshifts.symbolic import Alphabet, OneStepSFT

Matrix = tuple[tuple[int, ...], ...]
Transition = tuple[str, str]

LABELS = ("low", "baseline", "high")
TRAJECTORIES = (
    ("baseline", "high", "high", "baseline", "low", "low"),
    ("baseline", "high", "baseline", "low", "low", "baseline"),
    ("baseline", "baseline", "high", "baseline", "low", "baseline"),
    ("baseline", "high", "high", "baseline", "baseline", "low"),
)
MINIMUM_REPLICATE_SUPPORT = 2
PERIODS = (1, 2, 3, 4, 5, 6)


@dataclass(frozen=True, slots=True)
class TransitionEvidence:
    """Observed transition counts and the resulting binary adjacency matrix."""

    occurrence_counts: Matrix
    replicate_support: Matrix
    adjacency: Matrix


def infer_transition_evidence(
        trajectories: tuple[tuple[str, ...], ...],
        labels: tuple[str, ...],
        minimum_replicate_support: int,
) -> TransitionEvidence:
    """Infer allowed transitions supported by enough distinct replicates."""
    if not labels or len(set(labels)) != len(labels):
        raise ValueError("labels must be non-empty and unique")
    if not trajectories or any(len(trajectory) < 2 for trajectory in trajectories):
        raise ValueError("each trajectory must contain at least two states")
    if not 1 <= minimum_replicate_support <= len(trajectories):
        raise ValueError("minimum replicate support lies outside the replicate count")

    known_labels = set(labels)
    unknown = sorted({state for trajectory in trajectories for state in trajectory} - known_labels)
    if unknown:
        raise ValueError(f"unknown trajectory states: {', '.join(unknown)}")

    occurrences: Counter[Transition] = Counter()
    supporting_replicates: Counter[Transition] = Counter()
    for trajectory in trajectories:
        transitions = tuple(pairwise(trajectory))
        occurrences.update(transitions)
        supporting_replicates.update(set(transitions))

    occurrence_matrix = tuple(
        tuple(occurrences[(source, target)] for target in labels) for source in labels
    )
    support_matrix = tuple(
        tuple(supporting_replicates[(source, target)] for target in labels) for source in labels
    )
    adjacency = tuple(
        tuple(int(support >= minimum_replicate_support) for support in row)
        for row in support_matrix
    )
    return TransitionEvidence(occurrence_matrix, support_matrix, adjacency)


def build_response_summary() -> dict[str, Any]:
    """Build the example model and return a stable JSON-compatible summary."""
    evidence = infer_transition_evidence(
        TRAJECTORIES,
        LABELS,
        MINIMUM_REPLICATE_SUPPORT,
    )
    model = OneStepSFT.from_matrix(
        Alphabet(LABELS),
        evidence.adjacency,
        name="ERK response model",
    )
    signature = build_signature(model, periods=PERIODS)
    periodic_counts = tuple(int(value) for value in signature.feature("periodic_point_count"))
    least_period_counts = tuple(int(value) for value in signature.feature("least_period_count"))
    orbit_counts = tuple(
        count // period for period, count in zip(PERIODS, least_period_counts, strict=True)
    )

    transition_evidence = [
        {
            "source": source,
            "target": target,
            "occurrences": evidence.occurrence_counts[source_index][target_index],
            "replicate_support": evidence.replicate_support[source_index][target_index],
            "allowed": bool(evidence.adjacency[source_index][target_index]),
        }
        for source_index, source in enumerate(LABELS)
        for target_index, target in enumerate(LABELS)
        if evidence.occurrence_counts[source_index][target_index]
    ]

    return {
        "model": model.name,
        "alphabet": list(LABELS),
        "replicates": len(TRAJECTORIES),
        "minimum_replicate_support": MINIMUM_REPLICATE_SUPPORT,
        "adjacency": [list(row) for row in evidence.adjacency],
        "transition_evidence": transition_evidence,
        "periods": list(PERIODS),
        "periodic_point_count": list(periodic_counts),
        "least_period_count": list(least_period_counts),
        "least_period_orbit_count": list(orbit_counts),
        "guarantee": signature.guarantee.value,
        "interpretation_scope": "exact for the inferred finite transition model, not biology",
    }


def main() -> None:
    """Run the deterministic worked example."""
    print(json.dumps(build_response_summary(), indent=2))


if __name__ == "__main__":
    main()
