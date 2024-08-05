from datetime import datetime
from typing import Optional
from pydantic import BaseModel
import uuid
from ..models.books import FileType


class BookBaseSchema(BaseModel):
    user_id: uuid.UUID
    author: str
    title: str


class BookUploadResponseSchema(BookBaseSchema):
    id: uuid.UUID
    upload_date: datetime
    file_type: FileType
    original_file_name: str
    file_size: int


class BookResponseSchema(BookBaseSchema):
    id: uuid.UUID
    upload_date: datetime
    file_type: FileType
    cover_image_base64: Optional[str] = None


class BookUpdateSchema(BaseModel):
    author: str = None
    title: str = None
