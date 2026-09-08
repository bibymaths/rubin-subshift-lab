"""Configuration models and computational guarantee labels."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class AlgorithmicGuarantee(StrEnum):
    """Strength of the guarantee attached to a computational result."""

    EXACT_FINITE = "exact_finite"
    EXHAUSTIVE_WITHIN_BOUND = "exhaustive_within_bound"
    HEURISTIC = "heuristic"
    EXPERIMENTAL = "experimental"
    PROOF_GRADE = "proof_grade"


class ExperimentStatus(StrEnum):
    """Lifecycle state for an experiment."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    TRUNCATED = "truncated"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ComputationLimits(BaseModel):
    """Centralized upper bounds for combinatorial computations."""

    model_config = ConfigDict(frozen=True)

    max_alphabet_size: int = Field(default=6, ge=1, le=64)
    max_word_length: int = Field(default=20, ge=0, le=100)
    max_radius: int = Field(default=3, ge=0, le=10)
    max_period: int = Field(default=16, ge=1, le=100)
    max_configurations: int = Field(default=1_000_000, ge=1)
    max_local_rules: int = Field(default=100_000, ge=1)
    max_group_elements: int = Field(default=10_000, ge=1)
    max_graph_nodes: int = Field(default=5_000, ge=1)
    max_graph_edges: int = Field(default=25_000, ge=1)
    max_reconstruction_comparisons: int = Field(default=100, ge=1)
    max_inverse_candidates: int = Field(default=100_000, ge=1)
    max_execution_seconds: float = Field(default=30.0, gt=0)

    def state_space_size(self, alphabet_size: int, period: int) -> int:
        """Return an exact state-space size without materializing states."""
        return int(alphabet_size**period)

    def rule_space_size(self, alphabet_size: int, neighbourhood_size: int) -> int:
        """Return the number of total local rules for a neighbourhood."""
        return int(alphabet_size ** (alphabet_size**neighbourhood_size))
