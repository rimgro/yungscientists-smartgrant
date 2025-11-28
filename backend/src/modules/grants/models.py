import uuid
from typing import List

from sqlalchemy import Boolean, Column, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class GrantProgram(Base):
    __tablename__ = "grant_programs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(length=255), nullable=False)
    bank_account_number = Column(String(length=64), nullable=False)
    status = Column(String(length=50), default="draft", nullable=False)
    grantor_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    stages: Mapped[List["Stage"]] = relationship(
        "Stage", back_populates="grant_program", cascade="all, delete-orphan", order_by="Stage.order"
    )
    participants: Mapped[List["UserToGrant"]] = relationship(
        "UserToGrant", back_populates="grant_program", cascade="all, delete-orphan"
    )


class Stage(Base):
    __tablename__ = "stages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    grant_program_id = Column(UUID(as_uuid=True), ForeignKey("grant_programs.id", ondelete="CASCADE"), nullable=False)
    order = Column(Integer, nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    completion_status = Column(String(length=50), default="pending", nullable=False)

    grant_program: Mapped[GrantProgram] = relationship("GrantProgram", back_populates="stages")
    requirements: Mapped[List["Requirement"]] = relationship(
        "Requirement", back_populates="stage", cascade="all, delete-orphan"
    )


class Requirement(Base):
    __tablename__ = "requirements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    stage_id = Column(UUID(as_uuid=True), ForeignKey("stages.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(length=255), nullable=False)
    description = Column(String(length=500), nullable=True)
    status = Column(String(length=50), default="pending")

    stage: Mapped[Stage] = relationship("Stage", back_populates="requirements")


class UserToGrant(Base):
    __tablename__ = "user_to_grant"
    __table_args__ = (UniqueConstraint("user_id", "grant_program_id", name="uq_user_grant"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    grant_program_id = Column(UUID(as_uuid=True), ForeignKey("grant_programs.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(length=50), nullable=False)  # Grantor, Supervisor, Grantee
    active = Column(Boolean, default=True)

    grant_program: Mapped[GrantProgram] = relationship("GrantProgram", back_populates="participants")
