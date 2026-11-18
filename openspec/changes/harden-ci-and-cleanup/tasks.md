## 1. Runtime configuration (backend)

- [x] 1.1 Write `tests/test_config.py` covering each `runtime-configuration` secret scenario (`Settings(_env_file=None, ...)`, with `monkeypatch.delenv("SECRET_KEY")`). Verify that it fails before 1.2.
- [x] 1.2 Change the `SECRET_KEY` default to `"changethis"` and make the local warning say that the development default is in use. Verify that the tests in 1.1 pass, and that two `Settings()` objects without `SECRET_KEY` have the same key.
- [x] 1.3 Write `tests/test_cors.py` (preflight from a configured origin is allowed; from an unknown origin in `production`, no `Access-Control-Allow-Origin`). Then switch `app/main.py` CORS to `settings.all_cors_origins`, plus localhost:3000 in local mode (design Decision 6). Verify that the tests pass.

## 2. Health endpoint

- [x] 2.1 Write `tests/test_health.py` (200 with `{"status":"ok","database":"ok"}`; 503 with the fixed body and no exception text when the engine's `connect` raises; no auth needed). Verify that it fails first.
- [x] 2.2 Add `GET /health` (design Decision 1), and add `pool_pre_ping` plus a Postgres `connect_timeout` to the engine. Verify that the tests in 2.1 pass.

## 3. Migrations

- [x] 3.1 Delete the 5 revisions in `app/alembic/versions/` and the `backend/alembic/` folder, and add `import sqlmodel` to `script.py.mako`. Generate `0001_baseline` with autogenerate against an empty throwaway Postgres database, then review it (design Decision 3). Verify that `alembic upgrade head`, `alembic check`, `alembic downgrade base` and `alembic upgrade head` all succeed on an empty database.
- [x] 3.2 Write `tests/test_migrations.py` (marked `integration`; skipped unless `TEST_POSTGRES_URL` is set). It runs upgrade → check → downgrade base → upgrade against that URL and asserts the `user`/`file` tables and `file.yjs_state` exist. Verify that it passes with `TEST_POSTGRES_URL` pointing at a throwaway database, and is skipped without it.
- [x] 3.3 Add `backend/scripts/start.sh` (design Decision 4) and make both Dockerfiles use it, with the Python health check (Decision 1). Update `railway.json`, and change `setup-dev.sh` to run `alembic upgrade head` instead of `init_database.py`. Verify:
  - a backend container on an empty Postgres container creates the schema and becomes `healthy` in `docker inspect`;
  - with an unreachable database URL, the container exits non-zero without starting uvicorn.

## 4. Backend tests for auth and files

- [x] 4.1 Add a `fake_s3` fixture (design Decision 7), plus a test that the faked method names exist on the real S3 service. Verify that the test passes.
- [x] 4.2 Write `tests/test_auth.py`: signup, login success, wrong password rejected, `/users/me` without a token rejected. Verify that all pass.
- [x] 4.3 Write `tests/test_files.py`: upload, list, get, update content, delete as the owner, and user B gets 404 on get, content, update and delete for A's file. Verify that all pass, and `pytest --cov=app` shows `app/api/routes/files.py` covered by the tests.

- [x] 4.4 (Added at the user's request.) Fix the editor's Save: add owner-only `PUT /files/{id}` (filename and MIME type; unknown fields such as `content` ignored; blank filename → 422; bumps `updated_at`), returning `FilePublic`. Verify with tests: the editor's exact payload succeeds, a rename persists, `updated_at` increases, a blank name is rejected, and another user gets 404 and changes nothing.
- [x] 4.5 (Added at the user's request.) Make `POST /files/{id}/content` update `file_size`. Verify with a test that replaces the content and checks the new size and stored bytes.

## 5. Lint

- [x] 5.1 Fix the 9 existing flake8 findings in `backend/app` and `backend/tests`. Verify that `flake8 app tests` exits 0.
- [x] 5.2 Add `frontend/.eslintrc.cjs` (design Decision 9) and change the `lint`/`lint:fix` scripts. Fix ESLint errors in `src/` (correctness rules stay on). Verify that `npx eslint src --ext .vue,.js` exits 0 and `npm run build` succeeds.

## 6. Frontend API base and production build

- [x] 6.1 Change the `api.js` base URL to `${VITE_API_BASE_URL}/api/v1` with a same-origin fallback, and derive the `QuillEditor` collaboration URL default from `VITE_API_BASE_URL` when `VITE_COLLAB_WS` is unset (design Decision 6). Verify with two builds:
  - `VITE_API_BASE_URL=https://api.example.test npm run build`: `dist` contains `https://api.example.test` and no `wss://` default other than the derived one;
  - a build without the variable keeps `/api/v1` relative.
- [x] 6.2 Add `ARG`/`ENV` for `VITE_API_BASE_URL` and `VITE_COLLAB_WS` to `frontend/Dockerfile.prod`, and move them to `build.args` in `docker-compose.prod.yml`. Verify that `docker build --build-arg VITE_COLLAB_WS=wss://example.test/api/v1/collab -f frontend/Dockerfile.prod frontend` produces an image whose served JS contains that URL.

## 7. Local docker compose

- [x] 7.1 Make `vite.config.js` read `VITE_PROXY_TARGET` for both proxy entries. In `docker-compose.yml`:
  - fix `POSTGRES_PORT` to 5432;
  - backend `command: sh scripts/start.sh --reload`;
  - frontend `VITE_PROXY_TARGET=http://backend:8000`, and drop `VITE_API_BASE_URL`;
  - remove the init/`pg_hba`/config mounts and the custom db `command`.

  Then delete `pg_hba.conf`, `postgres.conf` and `postgresql.conf`. Verify that `docker compose config` is valid.
- [ ] 7.2 Run `docker compose up` from a clean state, using a compose project name or volume that doesn't touch any existing `postgres_data` volume. Verify:
  - `localhost:3000` serves the app and `localhost:8000/health` returns 200;
  - register and log in through the UI, then upload a document;
  - the owner and a share-link guest see each other's edits live in two browser tabs;
  - after `docker compose restart backend`, the edits are still there.

## 8. CI

- [x] 8.1 Replace `.github/workflows/deploy.yml` with `.github/workflows/ci.yml` (design Decision 8). Verify that the YAML parses, no step contains `|| true`, `|| echo`, `exit 0` or `--fix`, and the triggers include `push` to `prod`/`main` and `pull_request`.
- [ ] 8.2 Run every CI command locally in order (flake8; the Alembic sequence on a throwaway Postgres; pytest with coverage and `TEST_POSTGRES_URL`; ESLint; build; both production Docker builds). Verify that each exits 0. Then confirm that pytest with an empty tests folder exits non-zero, which shows the "no tests collected" scenario fails.

## 9. Repo cleanup and docs

- [x] 9.1 Untrack `frontend/dist` and `frontend/.DS_Store`, and delete the files listed in design Decision 10 after checking (with `grep`) that nothing else references them. Verify that `git status` shows the intended deletions only and `npm run build` and `pytest` still pass.
- [x] 9.2 Write `docs/deployment.md` from the seven deployment docs (design Decision 10), with the corrected env var meanings, then delete those docs. Verify that no file still links to a deleted doc (check with `grep`).
- [x] 9.3 Update the README:
  - CI badge for `ci.yml` on `prod`;
  - a "Running tests" section (`pytest`, `TEST_POSTGRES_URL`, `npm run lint`);
  - a quickstart pointing to `docker compose up`;
  - a link to `docs/deployment.md`;
  - remove the outdated "CI/CD Workflow" section.

  Verify that every command in the README runs as written.

## 10. Final verification

- [ ] 10.1 Run the full CI command list from 8.2 again after the cleanup, and record the results (and the coverage total) in the change notes.

## Progress notes

- **Paused 2026-11-17 at the user's request, after task 3.2.** Resume with `/opsx:apply harden-ci-and-cleanup`; the next task is 3.3 (the start script). Until 3.3 lands, containers still start uvicorn without running migrations. Run `alembic upgrade head` by hand.
- **Found during implementation:**
  - pydantic-settings 2.1.0 ignores `env_ignore_empty`, so an empty `SECRET_KEY` is handled by a field validator (design Decision 2 updated).
  - In Alembic 1.12 the exception is `alembic.util.AutogenerateDiffsDetected`.
  - `env.py` now accepts `config.attributes["database_url"]`, which lets tests point it at `TEST_POSTGRES_URL`.
- **Verified so far:**
  - pytest: 37 passed, 1 skipped (the Postgres migration test, which passes with `TEST_POSTGRES_URL`: 2 passed);
  - on an empty Postgres 15, the baseline runs up, `alembic check` finds nothing, then down and up again.
- **Session 2 (2026-11-17), tasks 3.3–7.1 done:**
  - The `.gitignore` rules (root and `backend/`) ignored every `test_*.py`, so the suite was never committed. Both are now scoped to ad-hoc scripts, with an exception for `**/tests/test_*.py`.
  - The production backend container migrated an empty Postgres and became `healthy`. With an unreachable database it exited 1 without starting uvicorn.
  - pytest: 57 passed, 1 skipped; coverage 72% total.
  - flake8 and ESLint (`--max-warnings 0`) are clean.
  - `docker compose up` (isolated project `fccheck`, database port not published because 5433 is taken locally): migrations ran, `/health` returned ok, the frontend served 200, and `/api/v1` was proxied to the backend.
  - The browser part of 7.2 was blocked: Docker Desktop stopped responding (`docker ps` hangs).
- **Found and then added as tasks 4.4 and 4.5 at the user's request:**
  - The editor's Save calls `PUT /files/{id}`, which doesn't exist, so Save stores the content and then shows "Failed to save file".
  - `POST /files/{id}/content` never updates `file_size` (an unused `new_file_size` was removed during the lint fixes).
- **Session 3 (2026-11-17):**
  - Tasks 4.4–4.5 (Save fix, file size), 8.1, 9.1–9.3 done.
  - Every CI step except the Docker builds was run locally in CI order against a throwaway PostgreSQL 17 database: flake8 ok; upgrade → check → downgrade → upgrade → downgrade ok; pytest 64 passed (including the migration tests), coverage 78%; `npm ci`, lint and build ok. pytest with no tests collected exits 5, so CI would fail it.
  - **Still blocked on Docker Desktop (`docker info` hangs):** the browser part of 7.2, the two image builds in 8.2, and 10.1.
- **Found, not fixed (outside this change):**
  - The backend ignores `DATABASE_URL`/`ENV`, which the old Render and Railway guides told you to set; `docs/deployment.md` now documents `POSTGRES_*`/`ENVIRONMENT`.
  - The README links to a `LICENSE` file that doesn't exist.
- **Session 4 (2026-11-19), both findings above fixed on `feature/database-url-and-license`:**
  - The backend now reads an optional `DATABASE_URL` (`postgres://`, `postgresql://` and `postgresql+psycopg2://` are normalized to psycopg2; anything else is rejected). When it is set, the `POSTGRES_*` variables are ignored. `ENV` is accepted as an alias for `ENVIRONMENT`, and `ENVIRONMENT` wins. Settings errors no longer echo the rejected values.
  - An MIT `LICENSE` file was added.
  - Verified: `tests/test_database_url.py` (12 tests) failed before the change and passes after it. Full suite on a throwaway PostgreSQL 14: 76 passed, coverage 78%. flake8 is clean. Alembic upgrade → check → downgrade → upgrade ran through `DATABASE_URL` alone, with `POSTGRES_SERVER` set to an unreachable host. `start.sh` with `ENV=production` + `DATABASE_URL` served `/health` → ok, and refused to start without `SECRET_KEY`.
  - Docker Desktop is still not running, so 7.2, the local part of 8.2, and 10.1 stay open.
