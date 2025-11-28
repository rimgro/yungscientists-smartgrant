from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from .schemas import GrantProgramCreate, GrantProgramRead, StageRead
from .services import GrantService

router = APIRouter(prefix="/grants", tags=["grants"])


@router.post("/", response_model=GrantProgramRead, status_code=status.HTTP_201_CREATED)
async def create_program(payload: GrantProgramCreate, session: AsyncSession = Depends(get_session)) -> GrantProgramRead:
    service = GrantService(session)
    return await service.create_program(payload)


@router.get("/", response_model=list[GrantProgramRead])
async def list_programs(session: AsyncSession = Depends(get_session)) -> list[GrantProgramRead]:
    service = GrantService(session)
    return await service.list_programs()


@router.post("/stages/{stage_id}/complete", response_model=StageRead)
async def complete_stage(stage_id: str, session: AsyncSession = Depends(get_session)) -> StageRead:
    service = GrantService(session)
    return await service.complete_stage(stage_id)
