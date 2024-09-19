from datetime import datetime
from typing import List, Optional
import uuid
from pydantic import BaseModel


class BookProcessResponseSchema(BaseModel):
    book_id: uuid.UUID
    is_requested: bool
    requested_at: Optional[datetime]
    completeness: Optional[float]
