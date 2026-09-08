"""Run small representative benchmarks without correctness thresholds."""

from __future__ import annotations

from time import perf_counter

from rubin_subshifts.cellular_automata import CellularAutomaton, analyze_finite_map


def main() -> None:
    """Print elapsed times for bounded reference operations."""
    for period in (6, 8, 10):
        start = perf_counter()
        result = analyze_finite_map(CellularAutomaton.elementary(110), period)
        elapsed = perf_counter() - start
        print({"period": period, "states": result.state_count, "seconds": elapsed})


if __name__ == "__main__":
    main()
