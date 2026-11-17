#!/bin/sh
# Start the backend: apply migrations, then hand the process over to uvicorn.
# Used by both Dockerfiles, docker-compose and railway.json. Extra arguments
# are passed to uvicorn (e.g. --reload for development).
set -eu

alembic upgrade head

# Single worker on purpose: collaboration rooms live in process memory
# (app/services/collab.py). exec makes uvicorn PID 1 so it receives SIGTERM
# and saves open documents on shutdown.
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}" "$@"
