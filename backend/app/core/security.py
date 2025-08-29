from datetime import datetime, timedelta, timezone
from typing import Any, cast

from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


ALGORITHM = "HS256"


def create_access_token(subject: str | Any, expires_delta: timedelta) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return cast(str, encoded_jwt)


def create_share_token(file_id: str, expires_delta: timedelta) -> str:
    """Create a short-lived token specifically for file sharing.

    Encodes the file id under the explicit claim "file_id" so it can be
    validated without parsing a stringified subject.
    """
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"exp": expire, "file_id": file_id}
    return cast(str, jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return cast(bool, pwd_context.verify(plain_password, hashed_password))


def get_password_hash(password: str) -> str:
    return cast(str, pwd_context.hash(password))
