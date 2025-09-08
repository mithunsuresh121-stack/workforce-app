# Contributing to Workforce App

## Branching Strategy

We follow a Git Flow inspired branching model:

- `main`: Production-ready code.
- `develop`: Integration branch for features and fixes.
- `feature/*`: New features branched off from `develop`.
- `bugfix/*`: Bug fixes for `develop`.
- `release/*`: Pre-production staging branches.
- `hotfix/*`: Urgent patches to `main`.

## Pull Request Process

- Always branch off from `develop` for features and bug fixes.
- Create a pull request (PR) to `develop` for review.
- PRs require at least one approval before merging.
- Use descriptive titles and link related issues.

## Commit Message Style

We use [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/):

- `feat:` A new feature
- `fix:` A bug fix
- `docs:` Documentation only changes
- `style:` Changes that do not affect the meaning of the code (white-space, formatting)
- `refactor:` A code change that neither fixes a bug nor adds a feature
- `test:` Adding missing tests or correcting existing tests
- `chore:` Changes to the build process or auxiliary tools

Example:

```
feat(auth): add JWT token refresh endpoint
fix(payroll): correct tax calculation for bonuses
```

Please ensure your code follows the project's coding standards and passes all tests before submitting a PR.
