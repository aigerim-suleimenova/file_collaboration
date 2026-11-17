## Purpose

Makes sure the backend runs with a stable token-signing secret: deployments must set one explicitly, while local development works without setup and doesn't log users out on every restart.

## ADDED Requirements

### Requirement: Deployed environments require an explicit secret
When `ENVIRONMENT` is `staging` or `production`, the backend SHALL refuse to start if `SECRET_KEY` is not set, is empty, or equals the development default. The error message SHALL name `SECRET_KEY` and SHALL NOT print any secret value.

#### Scenario: Production without SECRET_KEY
- **WHEN** the backend starts with `ENVIRONMENT=production` and no `SECRET_KEY`
- **THEN** startup fails with an error that names `SECRET_KEY`

#### Scenario: Production with the development default
- **WHEN** the backend starts with `ENVIRONMENT=production` and `SECRET_KEY` equal to the development default
- **THEN** startup fails with an error that names `SECRET_KEY`

#### Scenario: Production with a real secret
- **WHEN** the backend starts with `ENVIRONMENT=production` and a non-default `SECRET_KEY`
- **THEN** startup succeeds

### Requirement: Local development uses a stable secret
When `ENVIRONMENT` is `local` and `SECRET_KEY` is not set, the backend SHALL use a fixed development default and SHALL log a warning. Tokens issued before a restart SHALL remain valid after it, until they expire.

#### Scenario: Token survives a local restart
- **WHEN** a user logs in on a local backend with no `SECRET_KEY` set, and the backend process is restarted
- **THEN** requests with the previously issued access token are still accepted

#### Scenario: Warning in local mode
- **WHEN** a local backend starts without `SECRET_KEY`
- **THEN** a warning saying the development default is in use is emitted

### Requirement: Frontend calls the configured backend
The frontend SHALL send API requests to `${VITE_API_BASE_URL}/api/v1`, where `VITE_API_BASE_URL` is the backend's origin (for example `https://api.example.com`) and is fixed at build time. When `VITE_API_BASE_URL` is unset or empty, it SHALL use the frontend's own origin (`/api/v1`), so the dev-server proxy and same-origin deployments keep working.

#### Scenario: Standalone frontend build
- **WHEN** the frontend is built with `VITE_API_BASE_URL=https://api.example.test` and a user logs in
- **THEN** the login request goes to `https://api.example.test/api/v1/login/access-token`

#### Scenario: Collaboration URL follows the API base
- **WHEN** the frontend is built with `VITE_API_BASE_URL=https://api.example.test`, without `VITE_COLLAB_WS`, and a user opens a document in edit mode
- **THEN** the collaboration WebSocket connects to `wss://api.example.test/api/v1/collab/<file_id>`

#### Scenario: Same-origin default
- **WHEN** the frontend is built without `VITE_API_BASE_URL` and a user logs in
- **THEN** the login request goes to `/api/v1/login/access-token` on the frontend's own origin

### Requirement: Backend allows the configured browser origins
The backend's CORS policy SHALL allow exactly the origins in `BACKEND_CORS_ORIGINS` plus `FRONTEND_HOST`. In `local` it SHALL also allow `http://localhost:3000` and `http://127.0.0.1:3000`. Requests from other origins SHALL NOT receive `Access-Control-Allow-Origin`.

#### Scenario: Configured origin allowed
- **WHEN** the backend runs with `FRONTEND_HOST=https://app.example.test` and receives a CORS preflight from `https://app.example.test`
- **THEN** the response includes `Access-Control-Allow-Origin: https://app.example.test`

#### Scenario: Unknown origin rejected
- **WHEN** the backend runs with `ENVIRONMENT=production` and receives a CORS preflight from `https://evil.example.test`, which is not configured
- **THEN** the response does not include `Access-Control-Allow-Origin`
