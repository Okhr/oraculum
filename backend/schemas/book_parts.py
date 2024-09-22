from datetime import datetime
from typing import List, Optional
import uuid
from pydantic import BaseModel


class BookPartBaseSchema(BaseModel):
    id: uuid.UUID
    book_id: uuid.UUID
    parent_id: Optional[uuid.UUID] = None
    label: str
    created_at: datetime


class TocBookPartResponseSchema(BookPartBaseSchema):
    sibling_index: int
    is_story_part: bool
    children: Optional[List['TocBookPartResponseSchema']] = None


TocBookPartResponseSchema.model_rebuild()


class BookPartResponseSchema(BookPartBaseSchema):
    content: str
    sibling_index: int
    is_story_part: bool
    is_entity_extracted: bool
    created_at: datetime


class BookPartUpdateSchema(BaseModel):
    is_story_part: bool
