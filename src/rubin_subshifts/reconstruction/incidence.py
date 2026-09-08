"""Finite stabilizer-incidence summaries."""

from __future__ import annotations

import numpy as np

from rubin_subshifts.groups.permutations import Permutation


def fixed_point_incidence(elements: tuple[Permutation, ...]) -> np.ndarray:
    """Return the boolean element-by-point fixed-incidence matrix."""
    if not elements:
        return np.zeros((0, 0), dtype=bool)
    return np.asarray(
        [[element(point) == point for point in range(len(element))] for element in elements],
        dtype=bool,
    )
