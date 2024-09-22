from typing import List, Literal
import uuid
from pydantic import BaseModel

CategoryType = Literal['PERSON', 'LOCATION', 'ORGANIZATION', 'CONCEPT']


class Fact(BaseModel):
    book_part_id: uuid.UUID
    content: str
    sibling_index: int
    sibling_total: int


class EntityResponseSchema(BaseModel):
    name: str
    alternative_names: List[str]
    category: str
    facts: List[Fact]
