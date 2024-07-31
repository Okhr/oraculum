from typing import Annotated
from fastapi import APIRouter, Depends

from ..schemas import users as user_schemas
from ..database import get_db
from .auth import get_current_user


router = APIRouter()


@router.get("/me", response_model=user_schemas.UserResponseSchema)
async def read_users_me(current_user: Annotated[user_schemas.UserResponseSchema, Depends(get_current_user)]) -> user_schemas.UserResponseSchema:
    return current_user
