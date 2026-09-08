"""Bounded breadth-first closure of finite permutation generators."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

from rubin_subshifts.exceptions import DomainValidationError
from rubin_subshifts.groups.permutations import Permutation


@dataclass(frozen=True, slots=True)
class GeneratedGroup:
    """A completed or truncated finite permutation-group enumeration."""

    generators: tuple[Permutation, ...]
    elements: tuple[Permutation, ...]
    words: tuple[tuple[int, ...], ...]
    discovery_depths: tuple[int, ...]
    truncated: bool

    @property
    def order(self) -> int | None:
        """Return the group order only when closure completed."""
        return None if self.truncated else len(self.elements)


def generate_group(
    generators: tuple[Permutation, ...], max_elements: int = 10_000
) -> GeneratedGroup:
    """Enumerate generator closure with breadth-first word representatives."""
    if not generators:
        raise DomainValidationError("at least one generator is required")
    size = len(generators[0])
    if any(len(generator) != size for generator in generators):
        raise DomainValidationError("generators act on different set sizes")
    if max_elements < 1:
        raise DomainValidationError("max_elements must be positive")
    identity = Permutation.identity(size)
    elements = [identity]
    words: list[tuple[int, ...]] = [()]
    depths = [0]
    seen = {identity: 0}
    queue: deque[int] = deque([0])
    truncated = False
    while queue:
        current_index = queue.popleft()
        current = elements[current_index]
        for generator_index, generator in enumerate(generators):
            product_element = generator.compose(current)
            if product_element in seen:
                continue
            if len(elements) >= max_elements:
                truncated = True
                queue.clear()
                break
            seen[product_element] = len(elements)
            elements.append(product_element)
            words.append(words[current_index] + (generator_index,))
            depths.append(depths[current_index] + 1)
            queue.append(len(elements) - 1)
    return GeneratedGroup(generators, tuple(elements), tuple(words), tuple(depths), truncated)
