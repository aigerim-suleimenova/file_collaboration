## Why

Anyone reviewing this repository (for example a hiring team) will judge it by whether it builds, tests and runs as described. Today it doesn't:

- **CI hides failures:** it runs `pytest tests/ || echo "No tests found"`, ignores lint with `exit 0` (and has no ESLint config at all), and only triggers on `main` and `develop`, while the working branch is `prod`.
- **A fresh database can't be migrated:** `alembic upgrade head` fails at `update_file_schema_001`, because `5566abc09711` creates a table named `item`, not `file`. Nothing runs migrations on deploy either.
- **`SECRET_KEY` changes on every restart:** it defaults to a new random value per process, so every restart (and every `--reload`) logs everyone out, and tokens minted elsewhere are rejected.
- **Health checks fail:** the Docker health checks and `railway.json` call `/health`, which doesn't exist. `curl` isn't installed in `python:3.11-slim` either.
- **`docker compose up` is broken for local development:**
  - the backend uses database port `5433`, but Postgres listens on `5432` inside the network;
  - the frontend container's Vite proxy targets its own `localhost:8000`;
  - Postgres ignores the `init_database.py` mount (its init folder only runs `.sh`/`.sql` files);
  - mounting `pg_hba.conf` into the data directory interferes with first-time initialization.
- **`docker-compose.prod.yml` sets `VITE_*` variables when the container runs,** but Vite only reads them while building, so they have no effect.
- **A standalone frontend deployment can't reach the backend:**
  - `frontend/src/services/api.js` always calls the relative `/api/v1` and never reads `VITE_API_BASE_URL`;
  - the latest commit removed the backend proxy from the standalone Render frontend's nginx, so API calls hit the frontend host;
  - the backend's CORS list is hard-coded to localhost and ignores `BACKEND_CORS_ORIGINS` and `FRONTEND_HOST`.
- **Backend tests cover only collaboration:** auth and file access control have none.
- **The repo is cluttered:**
  - committed build output (`frontend/dist`) and `.DS_Store`;
  - five ad-hoc test pages and scripts (`frontend/test-*.html`, `frontend/test-room-connection.js`);
  - duplicate S3 scripts at the root;
  - two Alembic folders;
  - seven overlapping deployment documents, plus three frontend docs marked "Outdated" by the previous change.

## What Changes

- **Health endpoint:** add a `GET /health` endpoint that reports service and database status, and use it from the Docker health checks (no `curl` needed) and `railway.json`.
- **`SECRET_KEY`:**
  - make it explicit, and refuse to start outside `ENVIRONMENT=local` when it's missing or left at the default;
  - in local development, use a stable development default with a warning, so restarts don't log users out.
- **BREAKING (migrations only):** replace the broken migration chain with one baseline revision that creates the current schema from an empty database. Remove the unused duplicate `backend/alembic/` folder. Confirmed acceptable: there is no deployed database whose data must be kept.
- **Frontend API base:** the frontend calls `${VITE_API_BASE_URL}/api/v1`, falling back to the same origin when it's unset. `VITE_API_BASE_URL` now means the backend's origin, and the examples are corrected.
- **CORS:** the backend allows `BACKEND_CORS_ORIGINS` + `FRONTEND_HOST` (and localhost:3000 in local mode) instead of a hard-coded list.
- **Migrations on start:** run `alembic upgrade head` before uvicorn in every container and in `railway.json`, from a single start script.
- **Local `docker compose`:**
  - fix the database port;
  - make the Vite proxy target configurable (`VITE_PROXY_TARGET`) and set it to the backend service;
  - remove the ineffective and harmful Postgres mounts and config files;
  - give the backend a development `SECRET_KEY`;
  - result: `docker compose up` gives a working app with live collaboration.
- **Production compose:** pass `VITE_API_BASE_URL` and `VITE_COLLAB_WS` as build arguments to `frontend/Dockerfile.prod`.
- **Backend tests:** add tests for registration and login (including a wrong password), the file list/get/update/delete endpoints with S3 replaced by a fake, and the rule that user B cannot read or change user A's file. Also test `/health`, the `SECRET_KEY` startup rule, and migrations against Postgres.
- **CI** (`.github/workflows/ci.yml` replaces `deploy.yml`):
  - runs on pushes to `prod`/`main` and on pull requests;
  - backend: flake8, pytest with coverage against a Postgres service, `alembic upgrade head` then `alembic check`;
  - frontend: ESLint (new config) and `vite build`;
  - Docker: build both production images;
  - any failure fails the run, with no `|| echo`, `exit 0` or `--fix`.
- **Editor Save fix** (added at the user's request): add the missing `PUT /files/{id}` that the editor's Save button calls, and make replacing a file's content update `file_size`.
- **Lint fixes:** fix the existing 9 flake8 findings and any ESLint errors.
- **Repo cleanup:**
  - stop tracking `frontend/dist` and `.DS_Store`;
  - delete the ad-hoc test pages and scripts, root `aws_config.py`/`s3_operations.py`, `backend/test_auth.py` and `backend/create_test_user.py`, and the outdated Node-collab docs and scripts;
  - merge the deployment docs into `docs/deployment.md`.
- **README:** add a CI badge and a "Running tests" section.

## Capabilities

### New Capabilities
- `service-health`: a health endpoint that orchestrators and container health checks can use.
- `runtime-configuration`: startup rules for required secrets in each environment, how the frontend finds the backend, and which browser origins the backend allows.
- `database-migrations`: an empty database can be migrated to the current schema, migrations run on start, and the schema always matches the models.
- `continuous-integration`: what a CI run checks and when it must fail.
- `local-dev-environment`: `docker compose up` gives a working app, including live collaboration.

### Modified Capabilities
<!-- None: realtime-collaboration and document-content-safety are unchanged. -->

## Impact

- **Backend:**
  - `app/main.py` (`/health`);
  - `app/core/config.py` (`SECRET_KEY` rule);
  - `app/main.py` CORS from settings;
  - `app/alembic/versions/*` (replaced by a baseline);
  - `backend/alembic/` (removed);
  - `scripts/start.sh` (new);
  - `Dockerfile` and `Dockerfile.prod` (health check, start script);
  - small lint fixes in `app/`;
  - new tests in `tests/`.
- **Frontend:**
  - `.eslintrc.cjs` (new);
  - `vite.config.js` (`VITE_PROXY_TARGET`);
  - `src/services/api.js` (API base URL);
  - `Dockerfile.prod` (build arguments);
  - ESLint fixes in `src/`;
  - `dist/` no longer tracked.
- **Infrastructure:**
  - `docker-compose.yml` and `docker-compose.prod.yml`;
  - `railway.json`;
  - `.github/workflows/ci.yml` (replaces `deploy.yml`);
  - `pg_hba.conf`, `postgres.conf` and `postgresql.conf` removed.
- **Docs:**
  - `docs/deployment.md` replaces `DEPLOYMENT_CHECKLIST.md`, `DEPLOYMENT_SETUP.md`, `DEPLOY_NOW.md`, `DOCKER_README.md`, `RAILWAY_DEPLOYMENT.md`, `RENDER_DEPLOYMENT.md` and `RENDER_DOCKERFILE_FIX.md`;
  - the frontend `NODE18_SETUP.md`, `YJS_QUILL_INTEGRATION.md`, `test-collaboration.md` and `setup-node18.sh` are removed;
  - README updated.
- **Deploys:** a standalone frontend must be built with `VITE_API_BASE_URL=https://<backend-host>`, and the backend needs `FRONTEND_HOST`/`BACKEND_CORS_ORIGINS` set to the frontend's origin. Deploys must also set `SECRET_KEY` (and keep `ENVIRONMENT` non-local), or the backend refuses to start. Existing databases created by `create_all` would need `alembic stamp head` (none exist that matter).
- **Out of scope** (later changes): Vitest/Testing Library and Playwright, TypeScript, design tokens and Storybook.
