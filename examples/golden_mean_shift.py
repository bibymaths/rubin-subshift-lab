"""Print the first golden mean periodic-point counts."""

from rubin_subshifts.symbolic.sft import OneStepSFT

shift = OneStepSFT.golden_mean()
print([shift.periodic_point_count(period) for period in range(1, 11)])
