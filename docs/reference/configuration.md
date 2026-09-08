# Configuration reference

`ComputationLimits` centralizes caps for alphabet size, word length, radius, period, state count, local-rule count, group elements, graph size, inverse candidates, reconstruction comparisons, and wall-clock budgets.

```python
from rubin_subshifts.config import ComputationLimits

limits = ComputationLimits(max_period=12, max_group_elements=5_000)
assert limits.state_space_size(2, 12) == 4096
```

Before exhaustive enumeration, calculate the exact state-space size and compare it with the relevant limit. Counting never requires materializing the full space.

