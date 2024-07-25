from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
import uuid


class UserBaseSchema(BaseModel):
    name: str
    email: EmailStr


class CreateUserSchema(UserBaseSchema):
    password: str = Field(min_length=8)
    password_confirm: str = Field(min_length=8)


class UserResponseSchema(UserBaseSchema):
    id: uuid.UUID
    role: str
    created_at: datetime


class TokenSchema(BaseModel):
    access_token: str
    token_type: str
