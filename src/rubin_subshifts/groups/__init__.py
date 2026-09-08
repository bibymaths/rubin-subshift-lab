"""Finite permutation representations of automorphism actions."""

from rubin_subshifts.groups.finite_actions import induced_permutation
from rubin_subshifts.groups.generated_groups import GeneratedGroup, generate_group
from rubin_subshifts.groups.orbits import orbits, stabilizer
from rubin_subshifts.groups.permutations import Permutation

__all__ = [
    "GeneratedGroup",
    "Permutation",
    "generate_group",
    "induced_permutation",
    "orbits",
    "stabilizer",
]
