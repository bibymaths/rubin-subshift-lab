"""Validated experiment input and result models."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from rubin_subshifts.config import AlgorithmicGuarantee, ComputationLimits, ExperimentStatus


class ExperimentConfig(BaseModel):
    """Serializable configuration for a finite comparison experiment."""

    model_config = ConfigDict(frozen=True)

    left_example: str = "binary_full_shift"
    right_example: str = "golden_mean_shift"
    periods: tuple[int, ...] = (1, 2, 3, 4, 5, 6)
    random_seed: int = 0
    limits: ComputationLimits = Field(default_factory=ComputationLimits)

    @field_validator("periods")
    @classmethod
    def validate_periods(cls, value: tuple[int, ...]) -> tuple[int, ...]:
        """Require unique, increasing, positive periods."""
        if not value or any(period <= 0 for period in value):
            raise ValueError("periods must be positive")
        if tuple(sorted(set(value))) != value:
            raise ValueError("periods must be unique and increasing")
        return value

    @property
    def identifier(self) -> str:
        """Return a deterministic identifier for this configuration."""
        payload = json.dumps(self.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(payload.encode()).hexdigest()[:16]


@dataclass(frozen=True, slots=True)
class ExperimentResult:
    """Structured, serializable experiment outcome."""

    identifier: str
    status: ExperimentStatus
    summary: str
    guarantee: AlgorithmicGuarantee
    payload: dict[str, Any]
    error: str | None = None
