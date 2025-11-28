import uuid

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID

from src.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(length=255), nullable=False)
    email = Column(String(length=255), nullable=False, unique=True, index=True)
    hashed_password = Column(String(length=255), nullable=False)
    bank_id = Column(String(length=255), nullable=True)
