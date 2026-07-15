# Contributing

Contributions should preserve the dual-track design of this repository:

1. Keep `legacy` artifacts faithful to the recovered 2022 backup.
2. Put modern improvements in `core`, `analytics`, Python modules, and documentation.
3. Do not rewrite recovered legacy data in place.
4. Do not claim reconstructed scripts are the original 2022 source files.
5. Record provenance, assumptions, and limitations in `docs/`.

## Development Setup

```bash
cp .env.example .env
python -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
```

## Code Quality

- Use type hints for Python modules in `src/`.
- Keep SQL deterministic and readable.
- Prefer additive documentation over unstated assumptions.
- Add or update tests when behavior changes.

## Pull Requests

- Describe whether the change affects `legacy`, `core`, `analytics`, or documentation only.
- State whether any analytical result was recomputed from recovered data.
- Include screenshots for figure updates when practical.

