from typing import List, Literal
import uuid
from pydantic import BaseModel

CategoryType = Literal['PERSON', 'LOCATION', 'ORGANIZATION', 'CONCEPT']


class Fact(BaseModel):
    book_part_id: uuid.UUID
    content: str
    occurrences: int
    sibling_index: int | None
    sibling_total: int | None


class EntityResponseSchema(BaseModel):
    name: str
    alternative_names: List[str]
    category: str
    facts: List[Fact]
