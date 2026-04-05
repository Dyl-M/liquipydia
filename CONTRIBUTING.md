# Contributing to `liquipydia`

Thanks for your interest in contributing to **`liquipydia`**! Here are a few guidelines to help things go smoothly.

## Getting Started

1. Fork the repository and clone your fork.
2. Create a new branch from `dev` for your work:

   ```bash
   git checkout -b your-branch-name dev
   ```

3. Make your changes, then push to your fork and open a pull request targeting `dev`.

## Branch Strategy

The repository has two long-lived branches:

- `main` — always releasable, tagged for releases
- `dev` — integration branch for ongoing work

All work happens on short-lived branches created from `dev`. When `dev` is stable and ready for release, it is merged
into `main` via a pull request.

```
feat-xyz  ──► dev  ──► main
fix-abc   ──►     (PR + merge)
```

### Merge Strategy

PRs into `main` are **squash-merged** to keep the history clean (one commit per PR). The squash commit message must
follow [Conventional Commits](https://www.conventionalcommits.org/) format so that semantic release can determine
version bumps automatically.

Examples: `feat: add resource layer`, `fix: handle 429 rate limit`, `docs: update contributing guide`.

### Branch Naming

Use descriptive prefixes:

- `feat-*` for new features
- `fix-*` for bug fixes
- `docs-*` for documentation changes

## Pull Requests

- Keep PRs focused on a single change.
- Fill in the PR template when opening your pull request.
- Make sure CI checks pass before requesting review.

## Reporting Bugs & Requesting Features

- Use the [issue templates](https://github.com/Dyl-M/liquipydia/issues/new/choose) provided in the repository.
- For security vulnerabilities, follow the process described in [SECURITY.md](SECURITY.md).

## Code of Conduct

Be respectful and constructive. Harassment or abusive behavior will not be tolerated.

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).