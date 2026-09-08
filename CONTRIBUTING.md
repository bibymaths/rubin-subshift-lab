# Contributing

Contributions are welcome when they preserve the distinction between exact finite results and infinite-space claims.

1. Create a focused branch and describe the mathematical guarantee of new algorithms.
2. Install all groups with `uv sync --all-groups`.
3. Add unit, property, regression, and integration tests as appropriate.
4. Run the complete quality commands from `README.md`.
5. Update documentation and `CHANGELOG.md` for user-visible changes.

Do not add theorem citations, benchmark claims, or proof-grade labels without a verifiable source and documented assumptions. Keep optional GAP and SageMath adapters isolated from the core install.

