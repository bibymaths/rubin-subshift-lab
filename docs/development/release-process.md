# Release process

1. Update version metadata and `CHANGELOG.md`.
2. Run lint, formatting, typing, branch coverage, strict docs, and `uv build`.
3. Inspect wheel and source distribution contents.
4. Tag `vX.Y.Z` and push the tag.
5. The release workflow rebuilds, checksums, and attaches artifacts.

PyPI publication is intentionally absent until a trusted-publishing environment is explicitly configured.

