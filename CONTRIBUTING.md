# Contributing to `liquipydia`

Thanks for your interest in contributing to **`liquipydia`**! Here are a few guidelines to help things go smoothly.

## Getting Started

1. Fork the repository and clone your fork.
2. Create a new branch for your work. Branch from `dev` for code changes, or from `docs` for documentation-only changes:

   ```bash
   git checkout -b feat-your-feature dev    # code changes
   git checkout -b docs-your-update docs     # documentation-only changes
   ```

3. Install all development dependencies:

   ```bash
   uv sync --group dev
   ```

4. Make your changes, then push to your fork and open a pull request. Code changes target `dev`;
   documentation-only changes target `docs`.

## Development Commands

```bash
# Lint & format
uv run ruff check .              # lint
uv run ruff format --check .     # format check
uv run ruff check --fix .        # auto-fix lint issues
uv run ruff format .             # auto-format

# Type check
uv run mypy liquipydia

# Tests
uv run pytest                                            # full test suite
uv run coverage run -m pytest && uv run coverage report  # with coverage

# Documentation
uv sync --group docs                                               # install docs dependencies
uv run sphinx-build -b html _docs/sphinx _docs/sphinx/_build/html  # one-off build
uv run sphinx-autobuild _docs/sphinx _docs/sphinx/_build/html      # live preview with hot reload
```

## Branch Strategy

The repository has three long-lived branches:

- `main` — always releasable, tagged for releases, and the source the documentation site is built and deployed from
- `dev` — integration branch for ongoing code work
- `docs` — integration branch for documentation-only changes, branched from `main`

Code work happens on short-lived branches created from `dev`. When `dev` is stable and ready for release, it is merged
into `main` via a pull request.

Documentation-only work happens on short-lived branches created from `docs` (or directly on `docs` for maintainers). It
is merged straight into `main` via a pull request, bypassing `dev` — this keeps doc updates off the code integration
cycle while `main` stays the single deploy source. Since documentation commits use the `docs:` prefix, merging them into
`main` does not trigger a version bump.

After every push to `main`, the `Sync Branches` workflow (`.github/workflows/sync-branches.yml`) automatically
back-merges `main` into both `dev` and `docs`, so the release version bump reaches `dev` and `docs` stays current with
released code (keeping its autodoc-generated API reference fresh). If a back-merge hits a conflict the workflow fails
without pushing — resolve it locally with `git checkout <branch> && git merge origin/main`.

```
feat-xyz  ──► dev   ──► main
fix-abc   ──►      (PR + merge)

docs-xyz  ──► docs  ──► main
              (PR + merge, skips dev)
```

### Merge Strategy

| Target | Allowed merge methods | Notes                                               |
|--------|-----------------------|-----------------------------------------------------|
| `main` | **Squash only**       | One commit per release, linear history enforced     |
| `dev`  | **Squash or rebase**  | Linear history enforced, no merge commits           |
| `docs` | **Squash or rebase**  | Documentation-only changes, linear history enforced |

All commit messages (including squash commits) must follow
[Conventional Commits](https://www.conventionalcommits.org/) format so that semantic release can determine version bumps
automatically.

Examples: `feat: add resource layer`, `fix: handle 429 rate limit`, `docs: update contributing guide`.

### Branch Protection

`main`, `dev`, and `docs` are protected by rulesets:

- **No direct pushes to `main`** — all changes require a PR
- **Direct pushes to `dev` and `docs`** are allowed for repository maintainers only (e.g., changelog updates, quick
  fixes, small doc edits)
- **Required status checks** — `main` and `dev` both require `Lint & Format`, `Type Check`, and `Tests`; `main` also
  requires `Build Documentation`, so a broken docs build blocks any PR into `main`. The `docs` branch requires
  `Build Documentation` on PRs into it
- **`main` requires checks to be up to date** with the target branch before merging
- **No force pushes or branch deletion** on any of the three branches
- **Stale reviews are dismissed** on push to `main`
- **All review conversations must be resolved** before merging to `main`

### Branch Naming

Use descriptive prefixes:

- `feat-*` for new features (from `dev`)
- `fix-*` for bug fixes (from `dev`)
- `docs-*` for documentation changes (from `docs`)

## Pull Requests

- Keep PRs focused on a single change.
- Fill in the PR template when opening your pull request.
- Make sure CI checks pass before requesting review.

## Reporting Bugs & Requesting Features

- Use the [issue templates](https://github.com/Dyl-M/liquipydia/issues/new/choose) provided in the repository.
- For security vulnerabilities, follow the process described
  in [SECURITY.md](https://github.com/Dyl-M/liquipydia/blob/main/SECURITY.md).

## Code of Conduct

Be respectful and constructive. Harassment or abusive behavior will not be tolerated.

## License

By contributing, you agree that your contributions will be licensed under
the [MIT License](https://github.com/Dyl-M/liquipydia/blob/main/LICENSE).