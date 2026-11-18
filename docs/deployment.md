# Deployment

The app is two services and a database:

- **backend**: FastAPI (REST API, `/health`, and the real-time collaboration WebSocket at `/api/v1/collab/{file_id}`)
- **frontend**: a Vue single-page app, served by nginx in production
- **PostgreSQL 15**

The backend's start script (`backend/scripts/start.sh`) runs `alembic upgrade head` before starting uvicorn, so every deploy migrates the database first. If migrating fails, the server doesn't start.

## Environment variables

### Backend (runtime)

| Variable | Required | Meaning |
|---|---|---|
| `ENVIRONMENT` | yes, in deployments | `local`, `staging` or `production`. Outside `local`, a missing or default `SECRET_KEY` stops the backend from starting. `ENV` is accepted as an alias; `ENVIRONMENT` wins if both are set. |
| `SECRET_KEY` | yes, in deployments | Signs login and share tokens. Generate one with `python3 -c "import secrets; print(secrets.token_urlsafe(32))"`. Changing it logs everyone out. |
| `DATABASE_URL` | no | A full PostgreSQL URL (`postgres://`, `postgresql://` or `postgresql+psycopg2://`), as Render and Railway provide. When set, the `POSTGRES_*` variables below are ignored. |
| `POSTGRES_SERVER` | yes, without `DATABASE_URL` | Database host |
| `POSTGRES_PORT` | yes, without `DATABASE_URL` | Database port (usually `5432`) |
| `POSTGRES_USER` | yes, without `DATABASE_URL` | Database user |
| `POSTGRES_PASSWORD` | yes, without `DATABASE_URL` | Database password |
| `POSTGRES_DB` | yes, without `DATABASE_URL` | Database name |
| `FRONTEND_HOST` | yes | The frontend's origin, e.g. `https://app.example.com`. Allowed for CORS. |
| `BACKEND_CORS_ORIGINS` | no | Extra comma-separated origins allowed for CORS |
| `PORT` | no | Port to listen on (default `8000`). Most platforms set this. |
| `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`, `S3_BUCKET_NAME` | for uploads | S3 storage for uploaded files |

On Render or Railway, point `DATABASE_URL` at the provider's connection string (for example Railway's `${{Postgres.DATABASE_URL}}`). Otherwise set the separate `POSTGRES_*` variables.

Run exactly **one** backend instance and worker. Collaboration rooms live in the process's memory, so all editors of a document must reach the same process.

### Frontend (build time)

Vite bakes these into the JavaScript bundle when the image is **built**. Setting them on a running container has no effect.

| Variable | Meaning |
|---|---|
| `VITE_API_BASE_URL` | The backend's **origin**, e.g. `https://api.example.com` (no `/api` suffix). Leave empty when the frontend and backend share an origin through a reverse proxy. |
| `VITE_COLLAB_WS` | Optional. The collaboration WebSocket base. Defaults to `VITE_API_BASE_URL` with `http` changed to `ws` + `/api/v1/collab`, or to the page's own origin. |

## Local development (Docker Compose)

```bash
docker compose up --build
```

- App: http://localhost:3000. The Vite dev server proxies `/api/v1`, including WebSockets, to the backend.
- API: http://localhost:8000 (health check: http://localhost:8000/health)
- PostgreSQL: `localhost:5433` (user `postgres`, password `12345678`, database `file_collaboration_db`)

The schema is created automatically on first start. To start from an empty database again, run `docker compose down -v`.

## Production with Docker Compose (single host)

Create a `.env` next to `docker-compose.prod.yml` (see `env.production.example`). Then run:

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

`VITE_API_BASE_URL` and `VITE_COLLAB_WS` from `.env` are passed to the frontend image as build arguments.

## Render

Create three resources from the same repository and branch (`prod`).

1. **PostgreSQL**: create a database. Copy its **Internal Database URL** for the backend.
2. **Backend**, a Web Service with the Docker runtime:
   - **Root Directory:** `backend`
   - **Dockerfile Path:** `Dockerfile.prod`
   - **Build and Start Command:** leave empty (the Dockerfile runs migrations, then uvicorn)
   - **Health Check Path:** `/health`
   - **Environment:** `ENVIRONMENT=production`, `SECRET_KEY`, `DATABASE_URL` (the Internal Database URL), `FRONTEND_HOST=https://<frontend>.onrender.com`, and the S3 variables if you upload files
3. **Frontend**, a Web Service with the Docker runtime:
   - **Root Directory:** `frontend`
   - **Dockerfile Path:** `Dockerfile.prod`
   - **Environment:** `VITE_API_BASE_URL=https://<backend>.onrender.com`. Render passes environment variables to Docker builds as build arguments, and `Dockerfile.prod` declares them.

If the build fails with `failed to read dockerfile: open Dockerfile: no such file or directory`, the Root Directory or Dockerfile Path is missing.

After changing a frontend variable, **redeploy the frontend**, because the values are baked in at build time.

## Railway

`railway.json` deploys the backend with Nixpacks and starts it with `cd backend && sh scripts/start.sh` (migrate, then uvicorn on `$PORT`). Its health check path is `/health`.

1. Create a project from the GitHub repository, then add a PostgreSQL service.
2. On the backend service, set `ENVIRONMENT=production`, `SECRET_KEY`, `DATABASE_URL=${{Postgres.DATABASE_URL}}` (a reference to the PostgreSQL service's variable), and `FRONTEND_HOST`. Enable public networking.
3. Deploy the frontend separately (for example on Render as above, or as another Railway service using `frontend/Dockerfile.prod`), with `VITE_API_BASE_URL` set to the backend's public URL.

## Checking a deployment

- `GET https://<backend>/health` returns `{"status": "ok", "database": "ok"}`. A 503 means the backend can't reach the database: check `DATABASE_URL` or the `POSTGRES_*` values.
- Register, log in and upload a file through the frontend.
- Open the same document in two browsers (owner + share link). Edits should appear in both. If the editor says "Collaboration server unavailable", check `VITE_API_BASE_URL` / `VITE_COLLAB_WS` and redeploy the frontend.
- If the backend logs `SECRET_KEY is not set, so the development default is in use` and it won't start, set `SECRET_KEY`.
