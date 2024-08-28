from ..database import Base
from sqlalchemy import Column, String, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql.schema import ForeignKey
import uuid


class TextPart(Base):
    __tablename__ = 'book_parts'
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    book_id = Column(UUID(as_uuid=True), ForeignKey('book_files.id'), nullable=False)
    parent_id = Column(UUID(as_uuid=True), ForeignKey('book_parts.id'), nullable=True)
    toc_id = Column(String, nullable=False)
    label = Column(String, nullable=False)
    content = Column(String, nullable=False)
    sibling_index = Column(Integer, nullable=False)
