# CS Radar

Track growing topics in LLM research and explore papers through cited answers.
The repository currently contains project tooling; the research pipeline is not implemented yet.

## Development

Use Python 3.12 and [uv](https://docs.astral.sh/uv/).

```bash
uv sync --locked
uv run ruff check .
uv run ruff format --check .
uv run pytest
uv run cz check --message "chore: initialize project tooling"
```

There are no tests yet. Until tests are added, pytest reports no tests collected
and exits with code 5.

Use `uv run cz commit` to create a Conventional Commit when you are ready.
