import uuid
from typing import Annotated, Any

from fastapi import Depends
from sqlmodel import Session, select

from app.api.deps import get_db
from app.core.security import get_password_hash, verify_password
from app.models import FileCreate, FileUpdate, File, User, UserCreate
from app.services.s3_service import s3_service

SessionDep = Annotated[Session, Depends(get_db)]


# User CRUD helpers
def get_user_by_email(session: Session, email: str) -> User | None:
    return session.exec(select(User).where(User.email == email)).first()


def create_user(session: Session, user_create: UserCreate) -> User:
    user = User(
        email=user_create.email,
        hashed_password=get_password_hash(user_create.password),
        full_name=user_create.full_name,
        is_active=True,
        is_superuser=getattr(user_create, "is_superuser", False),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def authenticate(session: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(session, email=email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


# File CRUD helpers (File model)
def create_file_for_user(
    session: Session, *, owner_id: uuid.UUID, file_in: FileCreate
) -> File:
    file = File(
        filename=file_in.filename,
        s3_key=file_in.s3_key,
        file_size=file_in.file_size,
        mime_type=file_in.mime_type,
        original_format=file_in.original_format,
        quill_content=file_in.quill_content,
        owner_id=owner_id
    )
    session.add(file)
    session.commit()
    session.refresh(file)
    return file


def get_files_for_user(
    session: Session, *, owner_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> list[File]:
    statement = select(File).where(
        File.owner_id == owner_id).offset(skip).limit(limit)
    return list(session.exec(statement).all())


def get_file_by_id_for_user(
    session: Session, *, owner_id: uuid.UUID, file_id: uuid.UUID
) -> File | None:
    statement = select(File).where(
        File.owner_id == owner_id, File.id == file_id)
    return session.exec(statement).first()


def get_file_by_id(session: Session, *, file_id: uuid.UUID) -> File | None:
    """Fetch a file by id without checking ownership (use only after access checks)."""
    return session.get(File, file_id)


def update_file_for_user(
    session: Session, *, owner_id: uuid.UUID, file_id: uuid.UUID, file_in: FileUpdate
) -> File | None:
    file = get_file_by_id_for_user(session, owner_id=owner_id, file_id=file_id)
    if not file:
        return None
    update_data: dict[str, Any] = {}
    if file_in.filename is not None:
        update_data["filename"] = file_in.filename
    if file_in.mime_type is not None:
        update_data["mime_type"] = file_in.mime_type
    for key, value in update_data.items():
        setattr(file, key, value)
    session.add(file)
    session.commit()
    session.refresh(file)
    return file


def delete_file_for_user(
    session: Session, *, owner_id: uuid.UUID, file_id: uuid.UUID
) -> bool:
    file = get_file_by_id_for_user(session, owner_id=owner_id, file_id=file_id)
    if not file:
        return False
    session.delete(file)
    session.commit()
    return True
