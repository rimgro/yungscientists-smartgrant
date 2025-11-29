from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.core.security import get_current_user
from src.modules.auth.models import User
from .schemas import (
    GrantParticipantCreate,
    GrantParticipantRead,
    GrantParticipantRoleUpdate,
    GrantProgramCreate,
    GrantProgramRead,
    GrantBankAccountUpdate,
    RequirementProofSubmit,
    RequirementRead,
    StageRead,
)
from .services import GrantService

router = APIRouter(prefix="/grants", tags=["grants"])


def get_grant_service(session: AsyncSession = Depends(get_session)) -> GrantService:
    return GrantService(session)


@router.post("/", response_model=GrantProgramRead, status_code=status.HTTP_201_CREATED)
async def create_program(
    payload: GrantProgramCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> GrantProgramRead:
    service = GrantService(session)
    return await service.create_program(payload, current_user)


@router.get("/", response_model=list[GrantProgramRead])
async def list_programs(
    session: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)
) -> list[GrantProgramRead]:
    service = GrantService(session)
    return await service.list_programs(current_user)


@router.post("/{grant_program_id}/confirm", response_model=GrantProgramRead)
async def confirm_program(
    grant_program_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> GrantProgramRead:
    service = GrantService(session)
    return await service.confirm_program(grant_program_id, current_user)


@router.post("/{grant_program_id}/invite", response_model=list[GrantParticipantRead])
async def invite_participant(
    grant_program_id: str,
    payload: GrantParticipantCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> list[GrantParticipantRead]:
    service = GrantService(session)
    return await service.invite_participant(grant_program_id, payload, current_user)


@router.patch("/{grant_program_id}/participants/{participant_id}", response_model=list[GrantParticipantRead])
async def update_participant_role(
    grant_program_id: str,
    participant_id: str,
    payload: GrantParticipantRoleUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> list[GrantParticipantRead]:
    service = GrantService(session)
    return await service.update_participant_role(grant_program_id, participant_id, payload, current_user)


@router.delete("/{grant_program_id}/participants/{participant_id}", response_model=list[GrantParticipantRead])
async def remove_participant(
    grant_program_id: str,
    participant_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> list[GrantParticipantRead]:
    service = GrantService(session)
    return await service.remove_participant(grant_program_id, participant_id, current_user)


@router.post("/requirements/{requirement_id}/complete", response_model=RequirementRead)
async def complete_requirement(
    requirement_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> RequirementRead:
    service = GrantService(session)
    return await service.complete_requirement(requirement_id, current_user)


@router.post("/requirements/{requirement_id}/proof", response_model=RequirementRead)
async def submit_requirement_proof(
    requirement_id: str,
    payload: RequirementProofSubmit,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> RequirementRead:
    service = GrantService(session)
    return await service.submit_requirement_proof(requirement_id, payload, current_user)


@router.post("/stages/{stage_id}/complete", response_model=StageRead)
async def complete_stage(
    stage_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> StageRead:
    service = GrantService(session)
    return await service.complete_stage(stage_id, current_user)


@router.patch("/{grant_program_id}/bank-account", response_model=GrantProgramRead)
async def update_bank_account(
    grant_program_id: str,
    payload: GrantBankAccountUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> GrantProgramRead:
    service = GrantService(session)
    return await service.update_bank_account(grant_program_id, payload, current_user)
