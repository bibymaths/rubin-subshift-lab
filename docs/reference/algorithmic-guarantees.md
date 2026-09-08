# Algorithmic guarantees

| Enum | Interpretation |
| --- | --- |
| `EXACT_FINITE` | Mathematically exact on the explicitly represented finite domain |
| `EXHAUSTIVE_WITHIN_BOUND` | Every candidate inside declared finite bounds was considered unless marked truncated |
| `HEURISTIC` | Sampling or approximation without completeness |
| `EXPERIMENTAL` | A research proxy intended for exploration and conjecture formation |
| `PROOF_GRADE` | Reserved for complete, sourced algorithms under documented assumptions |

The current reconstruction comparison is experimental even when its component counts are exact finite values. A candidate inverse found by bounded search is validated on declared finite quotients; that evidence is not silently upgraded to a global inverse theorem.

