import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, JSON, String
from sqlalchemy.dialects.postgresql import UUID

from src.core.database import Base


class PaymentContract(Base):
    __tablename__ = "payment_contracts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(length=255), nullable=False)
    contract_type = Column(String(length=50), nullable=False)
    parameters = Column(JSON, nullable=False)
    description = Column(String(length=500), nullable=True)
    status = Column(String(length=50), default="active", nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
