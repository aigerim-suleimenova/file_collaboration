## Purpose

Gives load balancers, container runtimes and hosting platforms one reliable endpoint to tell whether the backend can serve requests.

## ADDED Requirements

### Requirement: Health endpoint reports service and database status
The backend SHALL serve `GET /health` without authentication.
- When the database is reachable, it SHALL respond `200` with JSON `{"status": "ok", "database": "ok"}`.
- When the database cannot be reached, it SHALL respond `503` with JSON `{"status": "error", "database": "unavailable"}`.

The response SHALL NOT include configuration values, credentials or error details.

#### Scenario: Healthy service
- **WHEN** a client sends `GET /health` while the database is reachable
- **THEN** the response status is 200 and the body is `{"status": "ok", "database": "ok"}`

#### Scenario: Database down
- **WHEN** a client sends `GET /health` while the database cannot be reached
- **THEN** the response status is 503 and the body is `{"status": "error", "database": "unavailable"}`, with no exception text

#### Scenario: No authentication needed
- **WHEN** a client sends `GET /health` without an `Authorization` header
- **THEN** the response is not 401 or 403

### Requirement: Container health checks use the health endpoint
Every backend container image SHALL declare a health check that calls `GET /health` with tools available in the image. The container SHALL be reported healthy when the service and database are up.

#### Scenario: Backend container becomes healthy
- **WHEN** the backend image is started with a reachable database
- **THEN** `docker inspect` reports the container's health status as `healthy` within the health check's start period plus three intervals
