"""Run the repository's release-readiness commands in sequence."""

from __future__ import annotations

import subprocess

COMMANDS = (
    ("uv", "run", "ruff", "check", "."),
    ("uv", "run", "ruff", "format", "--check", "."),
    ("uv", "run", "mypy", "src"),
    ("uv", "run", "pytest", "--cov=rubin_subshifts", "--cov-branch", "--cov-fail-under=90"),
    ("uv", "run", "zensical", "build", "--clean", "--strict"),
    ("uv", "build"),
)


def main() -> None:
    """Execute every validation command without shell interpolation."""
    for command in COMMANDS:
        subprocess.run(command, check=True)


if __name__ == "__main__":
    main()
