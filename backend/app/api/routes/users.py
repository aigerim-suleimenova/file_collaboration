import uuid
from typing import Any

from fastapi import APIRouter, HTTPException

from app import crud
from app.api.deps import CurrentUser, SessionDep
from app.models import User, UserCreate, UserPublic, UserRegister

router = APIRouter(prefix="/users", tags=["users"])


@router.options("/")
async def options_users():
    """Handle CORS preflight request"""
    return {"message": "OK"}


@router.options("/me")
async def options_users_me():
    """Handle CORS preflight request"""
    return {"message": "OK"}


@router.options("/{user_id}")
async def options_user_by_id():
    """Handle CORS preflight request"""
    return {"message": "OK"}


@router.post("/signup", response_model=UserPublic)
def register_user(session: SessionDep, user_in: UserRegister) -> Any:
    """
    Create new user without the need to be logged in.
    """
    user = crud.get_user_by_email(session=session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system",
        )
    user_create = UserCreate.model_validate(user_in)
    user = crud.create_user(session=session, user_create=user_create)
    return user


@router.get("/me", response_model=UserPublic)
def read_users_me(current_user: CurrentUser) -> Any:
    return current_user


@router.get("/{user_id}", response_model=UserPublic)
def read_user_by_id(
    user_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Get a specific user by id.
    """
    user = session.get(User, user_id)
    if user == current_user:
        return user
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="The user doesn't have enough privileges",
        )
    return user
