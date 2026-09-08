# Documentation development

Serve locally:

```bash
uv run zensical serve
```

Validate before committing:

```bash
uv run zensical build --clean --strict
```

`zensical.toml` uses Zensical-native TOML. Mermaid support is configured through `pymdownx.superfences`; API pages use the preliminary supported mkdocstrings plugin with `paths = ["src"]`.

