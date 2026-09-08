# Getting started

## Requirements

- Python 3.11 or newer
- [`uv`](https://docs.astral.sh/uv/)
- Optional: GAP for explicit exported permutation-group calculations

## Install

```bash
git clone https://github.com/<OWNER>/rubin-subshift-lab.git
cd rubin-subshift-lab
uv sync --all-groups
```

`uv.lock` fixes the complete environment. SageMath and GAP are not Python dependencies; adapters detect them at runtime.

## Launch the application

```bash
uv run streamlit run src/rubin_subshifts/app/streamlit_app.py
```

## First exact computation

```bash
uv run rubin-subshift subshift analyze --model golden-mean --max-period 10
```

The returned counts are exact for the listed finite periodic quotients. They do not enumerate the infinite shift space.

## Build documentation and package

```bash
uv run zensical build --clean --strict
uv build
```

