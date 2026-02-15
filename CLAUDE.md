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

### Workflow

```bash
# 1. Edit the notebook definitions
#    → scripts/generate_notebooks.py

# 2. Generate clean notebooks (no outputs)
uv run python scripts/generate_notebooks.py

# 3. Generate + execute (saves outputs for GitHub rendering)
uv run python scripts/generate_notebooks.py --execute

# 4. Force re-execution (even if already executed)
uv run python scripts/generate_notebooks.py --execute --force
```

Execution is **idempotent** — notebooks with existing outputs are skipped unless `--force` is passed. Requires `ENTSOE_API_KEY` in environment.
