from typing import List, Optional, Literal
from uuid import UUID

from pydantic import BaseModel, Field


class RequirementCreate(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = Field(None, max_length=500)


class RequirementRead(RequirementCreate):
    id: UUID
    status: str

    class Config:
        from_attributes = True


class StageCreate(BaseModel):
    order: int
    amount: float
    requirements: List[RequirementCreate] = Field(default_factory=list)


class StageRead(BaseModel):
    id: UUID
    order: int
    amount: float
    completion_status: str
    requirements: List[RequirementRead] = Field(default_factory=list)

    class Config:
        from_attributes = True


class GrantProgramCreate(BaseModel):
    name: str = Field(..., max_length=255)
    bank_account_number: str = Field(..., max_length=64)
    stages: List[StageCreate]
    participants: List["GrantParticipantCreate"] = Field(default_factory=list)


class GrantProgramRead(BaseModel):
    id: UUID
    name: str
    bank_account_number: str
    status: str
    participants: List["GrantParticipantRead"] = Field(default_factory=list)
    stages: List[StageRead] = Field(default_factory=list)

    class Config:
        from_attributes = True


class GrantParticipantCreate(BaseModel):
    user_id: str
    role: Literal["grantee", "supervisor"]


class GrantParticipantRead(BaseModel):
    id: UUID
    user_id: UUID
    grant_program_id: UUID
    role: str
    active: bool

    class Config:
        from_attributes = True


GrantProgramCreate.model_rebuild()
GrantProgramRead.model_rebuild()
