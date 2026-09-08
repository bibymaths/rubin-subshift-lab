# Command-line interface

```bash
uv run rubin-subshift --help
uv run rubin-subshift examples list
uv run rubin-subshift subshift analyze --model golden-mean
uv run rubin-subshift ca simulate --rule 110 --initial 00010000
uv run rubin-subshift ca finite-reversibility --rule 110 --period 8 --json
uv run rubin-subshift ca inverse-search --automaton left-shift
uv run rubin-subshift group explore --period 6 --json
uv run rubin-subshift reconstruction compare --max-period 10 --json
uv run rubin-subshift validate
```

Machine-readable commands accept `--json`. Failures use non-zero exit codes. `rubin-subshift app` launches Streamlit; `rubin-subshift docs build` runs strict Zensical validation.

