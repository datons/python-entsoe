# python-entsoe

Python client for the ENTSO-E Transparency Platform API.

## Environment

- **Python**: ≥3.13, managed with `uv`
- **API key**: stored in `.env` as `ENTSOE_API_KEY`
- Run scripts: `uv run python <script>`
- Run tests: `uv run pytest`

## Publishing

The repo lives in GitLab (`datons.com/libraries/python-entsoe`, private). Publishing is **tag-based only**: pushing to `main` does NOT release. The CI publishes to the `datons.com/libraries` package registry, which `esios` and the other services consume through the `datons-libraries` index.

```bash
# 1. Bump version in pyproject.toml
# 2. Commit the version bump
# 3. Tag and push
git tag v0.6.2
git push origin main --tags
```

The public GitHub/PyPI copy is no longer maintained.

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
