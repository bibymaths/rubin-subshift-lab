"""Repository documentation consistency checks."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).parents[2]


def test_required_documentation_and_examples_exist() -> None:
    required = (
        "README.md",
        "zensical.toml",
        "docs/index.md",
        "docs/reference/algorithmic-guarantees.md",
        "docs/development/testing.md",
        "examples/binary_full_shift.py",
        "examples/golden_mean_shift.py",
        "examples/elementary_ca.py",
        "examples/finite_group_action.py",
        "Dockerfile",
    )
    assert all((ROOT / path).is_file() for path in required)


def test_readme_commands_match_entry_points() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert 'rubin-subshift = "rubin_subshifts.cli:app"' in pyproject
    assert "uv run rubin-subshift --help" in readme
    assert "uv run zensical build --clean --strict" in readme
    assert "--cov-branch" in readme
