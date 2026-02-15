# python-entsoe

Python client for the ENTSO-E Transparency Platform API.

## Environment

- **Python**: ≥3.13, managed with `uv`
- **API key**: stored in `.env` as `ENTSOE_API_KEY`
- Run scripts: `uv run python <script>`
- Run tests: `uv run pytest`

## PyPI Publishing

Publishing is **tag-based only**. Pushing to `main` does NOT trigger a release.

```bash
# 1. Bump version in pyproject.toml
# 2. Commit the version bump
# 3. Tag and push
git tag v0.3.0
git push origin main --tags
```

The GitHub Actions workflow (`.github/workflows/publish.yml`) uses OIDC trusted publishing — no tokens needed.

## Example Notebooks

Notebooks in `examples/` are **generated** — do not edit them directly.

1. Edit `scripts/generate_notebooks.py`
2. Run `uv run python scripts/generate_notebooks.py`
3. Execute to verify: `export ENTSOE_API_KEY=... && uv run python -c "import nbformat; from nbclient import NotebookClient; nb = nbformat.read('examples/<name>.ipynb', as_version=4); NotebookClient(nb, timeout=120, kernel_name='python3').execute(); print('OK')"`
