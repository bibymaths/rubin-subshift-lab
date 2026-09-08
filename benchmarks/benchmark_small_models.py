"""Optional pytest-benchmark targets for representative small models."""

from rubin_subshifts.cellular_automata import CellularAutomaton, analyze_finite_map
from rubin_subshifts.symbolic.sft import OneStepSFT


def benchmark_periodic_counts() -> list[int]:
    """Return a small exact SFT count vector."""
    shift = OneStepSFT.golden_mean()
    return [shift.periodic_point_count(period) for period in range(1, 21)]


def benchmark_rule_110_period_eight() -> int:
    """Return the exact finite image size for a reference CA calculation."""
    return analyze_finite_map(CellularAutomaton.elementary(110), 8).image_count
