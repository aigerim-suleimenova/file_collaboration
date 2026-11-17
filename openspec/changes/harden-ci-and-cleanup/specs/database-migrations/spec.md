## Purpose

Makes sure any environment can build the database schema from nothing with one command, that the schema always matches the application's models, and that deployments apply migrations automatically.

## ADDED Requirements

### Requirement: Empty database migrates to the current schema
Running `alembic upgrade head` against an empty PostgreSQL database SHALL succeed and create every table, column and index defined by the application's models.

#### Scenario: Fresh database
- **WHEN** `alembic upgrade head` is run against an empty PostgreSQL database
- **THEN** it exits with status 0 and the `user` and `file` tables exist, including `file.yjs_state`

### Requirement: Schema matches the models
After `alembic upgrade head`, Alembic's autogenerate comparison against the models SHALL detect no differences.

#### Scenario: No pending model changes
- **WHEN** `alembic check` is run after `alembic upgrade head` on an empty database
- **THEN** it reports that no new upgrade operations were detected and exits with status 0

#### Scenario: Model changed without a migration
- **WHEN** a model column is added without a matching migration and `alembic check` is run
- **THEN** it exits with a non-zero status

### Requirement: Migrations can be rolled back to empty
Running `alembic downgrade base` after `alembic upgrade head` SHALL succeed and remove the application's tables.

#### Scenario: Full downgrade
- **WHEN** `alembic downgrade base` is run on a fully migrated database
- **THEN** it exits with status 0 and the `user` and `file` tables no longer exist

### Requirement: Migrations run before the server starts
Every way of starting the backend for deployment (both Dockerfiles and `railway.json`) SHALL apply `alembic upgrade head` before accepting requests. It SHALL NOT start the server if migrating fails.

#### Scenario: Container on an empty database
- **WHEN** a backend container starts against an empty database
- **THEN** the schema is created and `GET /health` then responds 200

#### Scenario: Migration failure
- **WHEN** a backend container starts and `alembic upgrade head` fails
- **THEN** the container exits with a non-zero status and uvicorn does not start
