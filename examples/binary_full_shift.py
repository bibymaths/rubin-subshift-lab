"""Enumerate a small periodic quotient of the binary full shift."""

from rubin_subshifts.symbolic.subshifts import binary_full_shift

shift = binary_full_shift()
print(["".join(map(str, point.word.symbols)) for point in shift.periodic_points(3)])
