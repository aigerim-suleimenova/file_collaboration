## Purpose

Defines what the repository's automated checks verify on every push and pull request, so a green run means the code lints, tests, migrates and builds.

## ADDED Requirements

### Requirement: CI runs on the branches that matter
The CI workflow SHALL run on every push to `prod` or `main` and on every pull request.

#### Scenario: Push to prod
- **WHEN** a commit is pushed to `prod`
- **THEN** a CI run starts for that commit

#### Scenario: Pull request
- **WHEN** a pull request is opened or updated
- **THEN** a CI run starts for its head commit

### Requirement: CI fails when any check fails
A CI run SHALL fail if any of these fail:
- backend lint (flake8);
- backend tests (pytest, against PostgreSQL);
- the migration checks (`alembic upgrade head` followed by `alembic check` on an empty PostgreSQL database);
- frontend lint (ESLint);
- the frontend production build;
- building either production Docker image.

No step SHALL hide a failure (for example with `|| echo`, `|| true` or `exit 0`), and lint SHALL NOT change files during CI.

#### Scenario: Failing test
- **WHEN** a commit makes any backend test fail
- **THEN** the CI run's status is failure

#### Scenario: No tests collected
- **WHEN** the backend test step collects zero tests
- **THEN** the CI run's status is failure

#### Scenario: Lint error
- **WHEN** a commit introduces a flake8 error in `backend/app` or an ESLint error in `frontend/src`
- **THEN** the CI run's status is failure

#### Scenario: Missing migration
- **WHEN** a commit changes a model without adding a migration
- **THEN** the CI run's status is failure

### Requirement: CI reports test coverage
The backend test step SHALL produce a coverage report for `app/`. The report SHALL appear in the run log.

#### Scenario: Coverage visible
- **WHEN** a CI run completes the backend test step
- **THEN** the log contains a per-file coverage table for `app/` with a total percentage
