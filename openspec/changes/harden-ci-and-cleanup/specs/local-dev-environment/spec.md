## Purpose

Makes the documented one-command local setup actually work, so a reviewer can run the whole app, including live collaboration, with `docker compose up`.

## ADDED Requirements

### Requirement: One command starts a working stack
From a clean checkout with no `.env` file, `docker compose up` SHALL start the database, backend and frontend. The database schema SHALL be created automatically, and the app SHALL be usable at `http://localhost:3000`.

#### Scenario: Clean start
- **WHEN** a developer runs `docker compose up` in a fresh clone with no existing compose volumes
- **THEN** within a few minutes `http://localhost:3000` serves the app, `http://localhost:8000/health` responds 200, and a new user can register and log in through the UI

### Requirement: Frontend reaches the backend inside compose
In the compose environment, browser requests to `/api/v1/...` (HTTP and WebSocket) on the frontend's dev server SHALL be forwarded to the backend service.

#### Scenario: API call through the dev server
- **WHEN** the browser at `http://localhost:3000` logs in
- **THEN** the login request is answered by the backend, and the files page loads the user's files

#### Scenario: Live collaboration in compose
- **WHEN** the owner and a share-link guest open the same document in two browsers against `docker compose up`
- **THEN** each sees the other's edits live, and the edits persist after `docker compose restart backend`

### Requirement: Production frontend image uses its build configuration
When the production frontend image is built with `VITE_API_BASE_URL` and `VITE_COLLAB_WS` provided as build arguments, the built assets SHALL use those values.

#### Scenario: Collaboration URL baked into the build
- **WHEN** the production frontend image is built with `VITE_COLLAB_WS=wss://example.test/api/v1/collab`
- **THEN** the served JavaScript contains `wss://example.test/api/v1/collab`
