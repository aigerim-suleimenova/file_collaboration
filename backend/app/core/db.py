from sqlmodel import create_engine

from app.core.config import settings

engine = create_engine(
    str(settings.SQLALCHEMY_DATABASE_URI),
    # Drop dead pooled connections instead of failing the next request, and fail
    # fast when the database is unreachable (so /health answers 503 promptly).
    pool_pre_ping=True,
    connect_args={"connect_timeout": 3},
)
