from typing import List, Optional, Literal
from uuid import UUID

from pydantic import BaseModel, Field, EmailStr, model_validator


class RequirementCreate(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = Field(None, max_length=500)


class RequirementRead(RequirementCreate):
    id: UUID
    status: str
    proof_url: Optional[str] = Field(None, max_length=500)
    proof_submitted_by: Optional[UUID]

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
    user_id: Optional[str] = None
    user_email: Optional[EmailStr] = None
    role: Literal["grantee", "supervisor"]

    @model_validator(mode="after")
    def ensure_identifier(self):
        if not self.user_id and not self.user_email:
            raise ValueError("Either user_id or user_email must be provided")
        return self


class GrantParticipantRead(BaseModel):
    id: UUID
    user_id: UUID
    grant_program_id: UUID
    role: str
    active: bool
    email: Optional[str] = None
    name: Optional[str] = None

    class Config:
        from_attributes = True


class GrantParticipantRoleUpdate(BaseModel):
    role: Literal["supervisor", "grantee"]


class RequirementProofSubmit(BaseModel):
    proof_url: str = Field(..., max_length=500)


GrantProgramCreate.model_rebuild()
GrantProgramRead.model_rebuild()
