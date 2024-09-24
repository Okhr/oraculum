from datetime import datetime
import uuid
from pydantic import BaseModel


class LightBookPartResponseSchema(BaseModel):
    id: uuid.UUID
    book_id: uuid.UUID
    parent_id: uuid.UUID | None
    label: str
    sibling_index: int
    is_story_part: bool
    is_entity_extracted: bool
    created_at: datetime
    level: int


class BookPartResponseSchema(LightBookPartResponseSchema):
    content: str


class BookPartUpdateSchema(BaseModel):
    is_story_part: bool
