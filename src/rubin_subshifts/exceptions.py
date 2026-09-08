"""Domain-specific exceptions."""

from __future__ import annotations


class RubinSubshiftError(Exception):
    """Base exception for package errors."""


class DomainValidationError(RubinSubshiftError, ValueError):
    """Raised when a mathematical object is malformed."""


class ComputationLimitError(RubinSubshiftError):
    """Raised before a computation would exceed a configured bound."""

    def __init__(self, operation: str, estimated: int, limit: int) -> None:
        self.operation = operation
        self.estimated = estimated
        self.limit = limit
        super().__init__(f"{operation} requires {estimated:,} items; configured limit is {limit:,}")


class ExportError(RubinSubshiftError):
    """Raised when a requested result export cannot be produced."""


class ExternalToolError(RubinSubshiftError):
    """Raised when an optional external integration fails."""
