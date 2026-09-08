"""One-dimensional cellular automata and finite reversibility analysis."""

from rubin_subshifts.cellular_automata.automata import CellularAutomaton
from rubin_subshifts.cellular_automata.local_rules import elementary_rule
from rubin_subshifts.cellular_automata.reversibility import (
    FiniteMapAnalysis,
    InverseSearchResult,
    analyze_finite_map,
    bounded_inverse_search,
)
from rubin_subshifts.cellular_automata.simulation import simulate

__all__ = [
    "CellularAutomaton",
    "FiniteMapAnalysis",
    "InverseSearchResult",
    "analyze_finite_map",
    "bounded_inverse_search",
    "elementary_rule",
    "simulate",
]
