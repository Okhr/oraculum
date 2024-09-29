from ..database import Base
from sqlalchemy import TIMESTAMP, Boolean, Column, String, Integer, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql.schema import ForeignKey
import uuid


class BookPart(Base):
    __tablename__ = 'book_parts'
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    book_id = Column(UUID(as_uuid=True), ForeignKey('book_files.id'), nullable=False)
    parent_id = Column(UUID(as_uuid=True), ForeignKey('book_parts.id'), nullable=True)
    toc_id = Column(String, nullable=False)
    label = Column(String, nullable=False)
    content = Column(String, nullable=False)
    sibling_index = Column(Integer, nullable=False)
    is_story_part = Column(Boolean, nullable=False, server_default=text("true"))
    is_entity_extracted = Column(Boolean, nullable=False, server_default=text("false"))
    sub_parts_count = Column(Integer, nullable=False, server_default=text("1"))
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
