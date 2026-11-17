from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import logging

import sentry_sdk
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy import text
from starlette.concurrency import run_in_threadpool
from starlette.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.core import log_redaction
from app.core.config import Settings, settings
from app.core.db import engine
from app.services.collab import collab_service


if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

log = logging.getLogger(__name__)

log_redaction.install()


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    # Runs the in-process Yjs collaboration server; saves open documents on shutdown.
    async with collab_service:
        yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    redirect_slashes=False,  # Prevent redirects that lose auth headers
)

LOCAL_DEV_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"]


def configure_cors(target: FastAPI, config: Settings) -> None:
    """Allow exactly the configured browser origins (plus the Vite dev server locally)."""
    origins = list(config.all_cors_origins)
    if config.ENVIRONMENT == "local":
        origins += [o for o in LOCAL_DEV_ORIGINS if o not in origins]
    target.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )


configure_cors(app, settings)

# Include your API routes
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "File Collaboration API", "docs": "/docs"}


def _database_reachable() -> bool:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception:
        log.exception("Health check: database unreachable")
        return False


@app.get("/health", include_in_schema=False)
async def health() -> JSONResponse:
    """Liveness + database readiness for container health checks and platforms."""
    if await run_in_threadpool(_database_reachable):
        return JSONResponse({"status": "ok", "database": "ok"})
    return JSONResponse({"status": "error", "database": "unavailable"}, status_code=503)
