from datetime import datetime, timedelta, timezone
import os
from typing import Annotated
from fastapi import APIRouter, Request, Response, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session
from jose import jwt, JWTError, ExpiredSignatureError

from backend.models import users as user_models

from backend.schemas import users as user_schemas

from backend import hashing
from backend.database import get_db


router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=int(os.getenv('ACCESS_TOKEN_EXPIRES_IN')))
    to_encode['exp'] = expire
    return jwt.encode(to_encode, os.getenv('SECRET_KEY'), os.getenv('JWT_ALGORITHM'))


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)) -> user_schemas.UserResponseSchema:
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=[os.getenv('JWT_ALGORITHM')])
        username = payload.get('sub')
        if username is None:
            raise credentials_exception
    except ExpiredSignatureError:
        raise HTTPException(status_code=403, detail="Token has been expired")
    except JWTError:
        raise credentials_exception

    user_in_db = db.query(user_models.User).filter(user_models.User.name == username).first()

    if not user_in_db:
        raise credentials_exception

    return user_schemas.UserResponseSchema(name=user_in_db.name, email=user_in_db.email, id=user_in_db.id, role=user_in_db.role, balance=user_in_db.balance, created_at=user_in_db.created_at)


@router.post('/register', status_code=status.HTTP_201_CREATED, response_model=user_schemas.UserResponseSchema)
async def create_user(payload: user_schemas.CreateUserSchema, db: Session = Depends(get_db)):
    user_in_db = db.query(user_models.User).filter(user_models.User.name == payload.name).first()
    if user_in_db:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f'User {payload.name} already exists')

    user_in_db = db.query(user_models.User).filter(user_models.User.email == payload.email).first()
    if user_in_db:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f'Email {payload.email} is already used')

    if payload.password != payload.password_confirm:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Passwords do not match')

    payload.password = hashing.hash_password(payload.password)
    del payload.password_confirm

    new_user = user_models.User(**payload.model_dump())

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post('/login', response_model=user_schemas.TokenSchema)
async def read_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)) -> user_schemas.TokenSchema:

    user_in_db = db.query(user_models.User).filter(user_models.User.name == form_data.username).first()

    if not user_in_db:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f'User {form_data.username} does not exist')

    if not hashing.verify_password(form_data.password, user_in_db.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Wrong password')

    access_token = create_access_token({'sub': user_in_db.name})
    return user_schemas.TokenSchema(access_token=access_token, token_type='bearer')
