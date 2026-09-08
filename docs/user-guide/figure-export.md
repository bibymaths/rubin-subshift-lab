# Figure export

Every principal visualization is a reusable Plotly `Figure`. Interactive HTML export is self-contained apart from the Plotly CDN. Static PNG, SVG, and PDF export uses Kaleido:

```python
from rubin_subshifts.visualization.export import export_figure

html = export_figure(figure, "html")
svg = export_figure(figure, "svg")
```

If the local Kaleido runtime cannot export, the package raises a focused `ExportError`; Streamlit should show that diagnostic rather than crash.

