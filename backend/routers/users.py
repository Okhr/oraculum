from typing import Annotated
from fastapi import APIRouter, Depends
from .. import schemas, models, hashing
from ..database import get_db
from .auth import get_current_user


router = APIRouter()


@router.get("/me", response_model=schemas.UserResponseSchema)
async def read_users_me(current_user: Annotated[schemas.UserResponseSchema, Depends(get_current_user)]) -> schemas.UserResponseSchema:
    return current_user
