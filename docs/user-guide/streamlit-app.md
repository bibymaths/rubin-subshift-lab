# Streamlit application

Launch with:

```bash
uv run streamlit run src/rubin_subshifts/app/streamlit_app.py
```

The application uses wide layout, persistent deterministic seeds, shared guarantee labels, resource estimates, Plotly figures, and downloadable evidence. Core algorithms live outside page modules so CLI and Python workflows execute the same logic.

No expensive exhaustive computation starts automatically. Pages either use small deterministic examples or wait for an explicit run button.

