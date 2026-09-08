"""Optional GAP interoperability with conservative subprocess handling."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from rubin_subshifts.exceptions import ExternalToolError
from rubin_subshifts.groups.permutations import Permutation


def gap_available() -> bool:
    """Return whether a GAP executable is available on ``PATH``."""
    return shutil.which("gap") is not None


def sage_available() -> bool:
    """Return whether a SageMath executable is available on ``PATH``."""
    return shutil.which("sage") is not None


def gap_script(generators: tuple[Permutation, ...]) -> str:
    """Return a narrowly scoped GAP program for the generator group size."""
    if not generators:
        raise ExternalToolError("cannot export an empty generator list")
    notation = ", ".join(generator.to_cycle_notation() for generator in generators)
    return f'G := Group([{notation}]);;\nPrint(Size(G), "\\n");\nQUIT;\n'


def sage_script(generators: tuple[Permutation, ...]) -> str:
    """Return a narrowly scoped SageMath program for a finite group size."""
    if not generators:
        raise ExternalToolError("cannot export an empty generator list")
    literals = ", ".join(repr(generator.to_cycle_notation()) for generator in generators)
    return (
        "from sage.all import Permutation, PermutationGroup\n"
        f"G = PermutationGroup([Permutation(value) for value in [{literals}]])\n"
        "print(G.order())\n"
    )


def write_gap_script(path: Path, generators: tuple[Permutation, ...]) -> Path:
    """Write a GAP-compatible generator script."""
    path.write_text(gap_script(generators), encoding="utf-8")
    return path


def write_sage_script(path: Path, generators: tuple[Permutation, ...]) -> Path:
    """Write a SageMath-compatible permutation-group script."""
    path.write_text(sage_script(generators), encoding="utf-8")
    return path


def run_gap_size(path: Path, timeout: float = 10.0) -> int:
    """Run an explicit GAP script and parse its single integer output."""
    executable = shutil.which("gap")
    if executable is None:
        raise ExternalToolError("GAP is not installed or not available on PATH")
    try:
        process = subprocess.run(
            [executable, "-q", str(path)],
            check=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except (subprocess.SubprocessError, OSError) as exc:
        raise ExternalToolError(f"GAP invocation failed: {exc}") from exc
    output = process.stdout.strip()
    if not output.isdigit():
        raise ExternalToolError(f"unexpected GAP output: {output!r}")
    return int(output)


def run_sage_size(path: Path, timeout: float = 10.0) -> int:
    """Run an explicit SageMath script and parse its single integer output."""
    executable = shutil.which("sage")
    if executable is None:
        raise ExternalToolError("SageMath is not installed or not available on PATH")
    try:
        process = subprocess.run(
            [executable, str(path)],
            check=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except (subprocess.SubprocessError, OSError) as exc:
        raise ExternalToolError(f"SageMath invocation failed: {exc}") from exc
    output = process.stdout.strip()
    if not output.isdigit():
        raise ExternalToolError(f"unexpected SageMath output: {output!r}")
    return int(output)
