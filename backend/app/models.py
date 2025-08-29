import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr
from sqlmodel import Field, Relationship, SQLModel


class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    files: list["File"] = Relationship(
        back_populates="owner", cascade_delete=True)


class File(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    filename: str = Field(max_length=255, index=True)
    s3_key: str | None = Field(default=None, max_length=500)  # S3 object key
    file_size: int | None = Field(default=None)  # File size in bytes
    mime_type: str | None = Field(default=None, max_length=100)  # File type
    # Original file format (docx, html, etc.)
    original_format: str | None = Field(default=None, max_length=20)
    # HTML content for Quill editor
    quill_content: str | None = Field(default=None)
    owner_id: uuid.UUID = Field(foreign_key="user.id", index=True)
    owner: User | None = Relationship(back_populates="files")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class UserPublic(BaseModel):
    id: uuid.UUID
    email: str  # include all fields you want to expose
    is_superuser: bool


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


class FileBase(SQLModel):
    filename: str = Field(max_length=255)
    mime_type: str | None = Field(default=None, max_length=100)


class FileCreate(FileBase):
    s3_key: str | None = Field(default=None, max_length=500)
    file_size: int | None = Field(default=None)
    original_format: str | None = Field(default=None, max_length=20)
    quill_content: str | None = Field(default=None)


class FileUpdate(SQLModel):
    filename: str | None = Field(default=None, max_length=255)
    mime_type: str | None = Field(default=None, max_length=100)


class FilePublic(BaseModel):
    id: uuid.UUID
    filename: str
    s3_key: str | None
    file_size: int | None
    mime_type: str | None
    original_format: str | None
    quill_content: str | None
    owner_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
