import uuid

from ..database import Base
from sqlalchemy import TIMESTAMP, Column, String, text
from sqlalchemy.dialects.postgresql import UUID


class User(Base):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False, server_default='user')
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
