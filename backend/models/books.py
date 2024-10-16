from ..database import Base
from sqlalchemy import TIMESTAMP, Boolean, Column, String, Integer, text
from sqlalchemy.dialects.postgresql import UUID, BYTEA
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import Enum
import uuid
import enum


class FileType(enum.Enum):
    epub = 1
    kindle = 2
    mobi = 3
    txt = 4
    rtf = 5


class Book(Base):
    __tablename__ = 'book_files'
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
    file_type = Column(Enum(FileType), nullable=False)
    original_file_name = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    file_data = Column(BYTEA, nullable=False)
    author = Column(String, nullable=False)
    title = Column(String, nullable=False)
    data_hash = Column(String, nullable=False)
    cover_image_base64 = Column(String, nullable=True)
    is_parsed = Column(Boolean, nullable=False, server_default=text("false"))
    extraction_start_time = Column(TIMESTAMP(timezone=True), nullable=True)
