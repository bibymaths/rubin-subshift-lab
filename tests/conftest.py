"""Shared deterministic test fixtures."""

from __future__ import annotations

import pytest

from rubin_subshifts.symbolic import Alphabet


@pytest.fixture
def binary() -> Alphabet:
    """Return the canonical binary alphabet."""
    return Alphabet((0, 1))
