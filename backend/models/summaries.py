from backend.database import Base
from sqlalchemy import TIMESTAMP, Column, String, Integer, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql.schema import ForeignKey
import uuid


class Summary(Base):
    __tablename__ = 'summaries'
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    book_id = Column(UUID(as_uuid=True), ForeignKey('book_files.id'), nullable=False)
    book_part_id = Column(UUID(as_uuid=True), ForeignKey('book_parts.id'), nullable=False)
    content = Column(String, nullable=False)
    sibling_index = Column(Integer, nullable=True)
    sibling_total = Column(Integer, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
