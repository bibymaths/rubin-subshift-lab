# Testing

Run the branch-aware suite:

```bash
uv run pytest \
  --cov=rubin_subshifts \
  --cov-branch \
  --cov-report=term-missing \
  --cov-report=xml \
  --cov-report=html \
  --cov-fail-under=90
```

Tests cover validation, exact encodings, regression examples, permutation laws, finite group closure, bounded errors, CLI flows, figure construction, serialization, and Streamlit smoke behaviour. Optional GAP and static-export tests skip only when their external runtime is unavailable.

