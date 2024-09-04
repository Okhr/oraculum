from ..database import Base
from sqlalchemy import TIMESTAMP, Column, String, Integer, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql.schema import ForeignKey
import uuid


class KnowledgeBaseEntry(Base):
    __tablename__ = 'knowledge_base_entries'
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    book_id = Column(UUID(as_uuid=True), ForeignKey('book_files.id'), nullable=False)
    book_part_id = Column(UUID(as_uuid=True), ForeignKey('book_parts.id'), nullable=False)
    entity_name = Column(String, nullable=False)
    alternative_names = Column(String, nullable=True)  # comma separated list of alternative names
    referenced_entity_name = Column(String, nullable=True)
    category = Column(String, nullable=False)
    fact = Column(String, nullable=False)
    sibling_index = Column(Integer, nullable=False)
    sibling_total = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
