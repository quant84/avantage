# Contributing to avantage

Thank you for your interest in contributing. This document covers the development workflow, code standards, and process for submitting changes.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Code Style](#code-style)
- [Pull Requests](#pull-requests)
- [Reporting Bugs and Requesting Features](#reporting-bugs-and-requesting-features)

---

## Getting Started

### Prerequisites

- Python 3.11 or later
- `git`
- A GitHub account

### Fork and Clone

1. Fork the repository at [github.com/quant84/avantage](https://github.com/quant84/avantage) using the GitHub UI.
2. Clone your fork locally:

   ```bash
   git clone https://github.com/<your-username>/avantage.git
   cd avantage
   ```

3. Add the upstream remote so you can stay in sync with the canonical repository:

   ```bash
   git remote add upstream https://github.com/quant84/avantage.git
   ```

### Install Development Dependencies

Create and activate a virtual environment, then install the package in editable mode with all development dependencies:

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install -e ".[dev]"
```

### Run the Test Suite

Verify your environment is working before making any changes:

```bash
pytest
```

All tests should pass on a clean checkout. If they do not, open an issue before proceeding.

---

## Development Workflow

### Staying Up to Date

Before starting any new work, pull the latest changes from upstream:

```bash
git fetch upstream
git rebase upstream/main main
```

### Branch Naming

Create a feature branch from `main`. Use a short, descriptive name that reflects the scope of the change:

| Type | Pattern | Example |
|------|---------|---------|
| New feature | `feat/<description>` | `feat/options-endpoint` |
| Bug fix | `fix/<description>` | `fix/rate-limit-retry` |
| Documentation | `docs/<description>` | `docs/contributing` |
| Refactor | `refactor/<description>` | `refactor/client-transport` |
| Tests | `test/<description>` | `test/forex-coverage` |

```bash
git checkout -b feat/your-feature-name
```

### Commits

Write commit messages in the imperative mood and keep the subject line under 72 characters. Reference relevant issues where applicable.

```
Add retry logic for 429 rate-limit responses

Implements exponential backoff with jitter when the API returns HTTP 429.
Closes #42.
```

Commit logical units of work separately rather than bundling unrelated changes into a single commit.

### Running Checks Locally

Run all checks before pushing. CI enforces these on Python 3.11, 3.12, and 3.13, so catching failures locally saves time.

**Tests:**

```bash
pytest
```

For verbose output or to run a specific module:

```bash
pytest -v tests/test_equity.py
```

**Linting:**

```bash
ruff check .
ruff format --check .
```

To auto-fix lint and formatting issues:

```bash
ruff check --fix .
ruff format .
```

**Type checking:**

```bash
mypy --strict .
```

The mypy configuration includes the Pydantic v2 plugin. All type errors must be resolved; `type: ignore` suppressions require an inline comment explaining why they are necessary.

---

## Code Style

### General Principles

- **Async-first.** All I/O-bound operations must be `async`. Blocking calls inside coroutines are not acceptable.
- **Type everything.** All function signatures, including return types, must be fully annotated. `Any` should be avoided; if it is genuinely necessary, explain why with a comment.
- **No broad exception handling.** Do not catch `Exception` or `BaseException` unless you immediately re-raise or have a documented rationale. Catch the narrowest exception type that applies.
- **Pydantic v2 models for data.** API response shapes are represented as `pydantic.BaseModel` subclasses. Do not use plain `dict` as a public return type.
- **httpx for HTTP.** The async `httpx.AsyncClient` is the sole HTTP transport. Do not introduce additional HTTP libraries.

### Linting and Formatting

The project uses [Ruff](https://docs.astral.sh/ruff/) for both linting and formatting. Configuration lives in `pyproject.toml`. Do not bypass ruff rules with `# noqa` unless the suppression is genuinely warranted and accompanied by a comment.

### Type Checking

Mypy runs with `--strict`, which enables all optional error codes including `disallow_untyped_defs`, `disallow_any_generics`, and `warn_return_any`. The Pydantic plugin is active, so Pydantic models are understood natively by mypy without manual stubs.

### Testing

- Tests live under `tests/` and mirror the package structure.
- Use `pytest-asyncio` for async test functions (mark with `@pytest.mark.asyncio`).
- HTTP calls must be mocked with `respx`. No test should make a real network request.
- Aim for meaningful coverage of both success paths and error/edge cases.
- Fixtures belong in `conftest.py` at the appropriate directory level.

---

## Pull Requests

### Before Opening a PR

- Rebase your branch on the latest `upstream/main` to avoid merge conflicts.
- Confirm all tests pass, `ruff check` reports no issues, `ruff format --check` reports no diff, and `mypy --strict` exits cleanly.
- If your change touches public API surface, update the relevant docstrings and any affected examples.

### What to Include

A good pull request:

- Has a clear title that summarises the change (same conventions as commit messages).
- Includes a description that explains **what** changed and **why**, not just **how**.
- References any related issues (`Closes #<n>` or `Relates to #<n>`).
- Keeps scope focused. Separate unrelated changes into separate PRs.
- Adds or updates tests to cover the changed behaviour.

### Review and Merge Process

- PRs are opened against the `main` branch.
- CI must pass across all supported Python versions (3.11, 3.12, 3.13) before a PR can be merged.
- At least one maintainer approval is required.
- PRs are merged using squash merge. Ensure your commit history on the branch is reasonably clean, as the squash commit message is derived from the PR title and description.

---

## Reporting Bugs and Requesting Features

Use [GitHub Issues](https://github.com/quant84/avantage/issues) for both bug reports and feature requests.

### Bug Reports

A useful bug report includes:

- The version of `avantage` and Python you are using.
- A minimal, self-contained code example that reproduces the problem.
- The full traceback or unexpected output you observed.
- What you expected to happen instead.

### Feature Requests

Before opening a feature request, search existing issues to avoid duplicates. When opening one, describe the use case you are trying to address rather than jumping straight to a proposed implementation. This makes it easier to discuss scope and design before any code is written.

---

For questions that do not fit neatly into a bug report or feature request, open a GitHub Discussion.
