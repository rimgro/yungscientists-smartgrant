from typing import List, Optional

from pydantic import BaseModel, Field


class RequirementCreate(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = Field(None, max_length=500)


class RequirementRead(RequirementCreate):
    id: str
    status: str

    class Config:
        from_attributes = True


class StageCreate(BaseModel):
    order: int
    amount: float
    requirements: List[RequirementCreate] = []


class StageRead(BaseModel):
    id: str
    order: int
    amount: float
    completion_status: str
    requirements: List[RequirementRead] = []

    class Config:
        from_attributes = True


class GrantProgramCreate(BaseModel):
    name: str = Field(..., max_length=255)
    grant_receiver: str = Field(..., max_length=255)
    stages: List[StageCreate]


class GrantProgramRead(BaseModel):
    id: str
    name: str
    grant_receiver: str
    stages: List[StageRead] = []

    class Config:
        from_attributes = True
