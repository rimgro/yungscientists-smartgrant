from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.auth.models import User
from src.modules.auth.repositories import UserRepository
from src.core.config import settings
from src.modules.payments.services import PaymentService
from .models import GrantProgram, Requirement, Stage, UserToGrant
from .repositories import GrantRepository
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


class GrantService:
    def __init__(self, session: AsyncSession, payment_service: PaymentService | None = None):
        self.session = session
        self.repo = GrantRepository(session)
        self.payment_service = payment_service or PaymentService()
        self.user_repo = UserRepository(session)

    async def create_program(self, payload: GrantProgramCreate, current_user: User) -> GrantProgramRead:
        self._validate_stage_order(payload)

        program = GrantProgram(
            name=payload.name,
            bank_account_number=payload.bank_account_number,
            grantor_id=current_user.id,
        )
        program.participants.append(UserToGrant(user_id=current_user.id, role="grantor"))

        unique_participants: dict[UUID, GrantParticipantCreate] = {}
        for participant in payload.participants:
            resolved_id = await self._resolve_user_identifier(participant)
            if resolved_id in unique_participants:
                continue
            if resolved_id == current_user.id:
                continue
            unique_participants[resolved_id] = participant

        for participant_id, participant in unique_participants.items():
            program.participants.append(UserToGrant(user_id=participant_id, role=participant.role))

        for stage_payload in sorted(payload.stages, key=lambda s: s.order):
            stage = Stage(order=stage_payload.order, amount=stage_payload.amount)
            for req_payload in stage_payload.requirements:
                requirement = Requirement(name=req_payload.name, description=req_payload.description)
                stage.requirements.append(requirement)
            program.stages.append(stage)

        await self.repo.create(program)
        await self.session.commit()
        reloaded = await self.repo.get(program.id)
        return GrantProgramRead.model_validate(reloaded, from_attributes=True)

    async def list_programs(self, current_user: User) -> list[GrantProgramRead]:
        programs = await self.repo.list_for_user(current_user.id)
        return [GrantProgramRead.model_validate(p) for p in programs]

    async def confirm_program(self, grant_program_id: str, current_user: User) -> GrantProgramRead:
        program_id = self._parse_uuid(grant_program_id)
        program = await self.repo.get(program_id)
        if not program:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grant not found")

        self._ensure_role(program, current_user, allowed_roles=["grantor"])
        if program.status != "draft":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Grant already confirmed")
        if not program.stages:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Stages must be configured")

        total_amount = sum(float(stage.amount) for stage in program.stages)
        deposit_result = await self.payment_service.deposit_grant(
            participant_id=settings.app_bank_account_number, amount=total_amount
        )
        if deposit_result.status != "deposited":
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Grant deposit failed")

        program.status = "active"
        for index, stage in enumerate(sorted(program.stages, key=lambda s: s.order)):
            stage.completion_status = "active" if index == 0 else "pending"

        await self.session.commit()
        reloaded = await self.repo.get(program.id)
        return GrantProgramRead.model_validate(reloaded, from_attributes=True)

    async def invite_participant(
        self, grant_program_id: str, payload: GrantParticipantCreate, current_user: User
    ) -> list[GrantParticipantRead]:
        program_id = self._parse_uuid(grant_program_id)
        program = await self.repo.get(program_id)
        if not program:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grant not found")

        self._ensure_role(program, current_user, allowed_roles=["grantor"])
        if payload.user_id == str(current_user.id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Grantor already assigned")

        participant_uuid = await self._resolve_user_identifier(payload)
        existing = next((p for p in program.participants if p.user_id == participant_uuid), None)
        if existing:
            if not existing.active:
                existing.active = True
                existing.role = payload.role
            else:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already invited to grant")
        else:
            program.participants.append(UserToGrant(user_id=participant_uuid, role=payload.role))

        await self.session.commit()
        reloaded = await self.repo.get(program.id)
        return [GrantParticipantRead.model_validate(p, from_attributes=True) for p in reloaded.participants]

    async def update_participant_role(
        self, grant_program_id: str, participant_id: str, payload: GrantParticipantRoleUpdate, current_user: User
    ) -> list[GrantParticipantRead]:
        program_id = self._parse_uuid(grant_program_id)
        participant_uuid = self._parse_uuid(participant_id)
        program = await self.repo.get(program_id)
        if not program:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grant not found")

        self._ensure_role(program, current_user, allowed_roles=["grantor"])
        participant = next((p for p in program.participants if p.id == participant_uuid), None)
        if not participant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Participant not found")
        if participant.role == "grantor":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot change grantor role")
        participant.role = payload.role
        await self.session.commit()
        reloaded = await self.repo.get(program.id)
        return [GrantParticipantRead.model_validate(p, from_attributes=True) for p in reloaded.participants]

    async def remove_participant(
        self, grant_program_id: str, participant_id: str, current_user: User
    ) -> list[GrantParticipantRead]:
        program_id = self._parse_uuid(grant_program_id)
        participant_uuid = self._parse_uuid(participant_id)
        program = await self.repo.get(program_id)
        if not program:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grant not found")

        self._ensure_role(program, current_user, allowed_roles=["grantor"])
        if program.grantor_id == participant_uuid:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot remove grantor")

        participant = next((p for p in program.participants if p.id == participant_uuid), None)
        if not participant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Participant not found")

        await self.session.delete(participant)
        await self.session.commit()
        reloaded = await self.repo.get(program.id)
        return [GrantParticipantRead.model_validate(p, from_attributes=True) for p in reloaded.participants]

    async def complete_requirement(self, requirement_id: str, current_user: User) -> RequirementRead:
        requirement_uuid = self._parse_uuid(requirement_id)
        requirement = await self.repo.get_requirement(requirement_uuid)
        if not requirement:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Requirement not found")

        program = requirement.stage.grant_program
        self._ensure_role(program, current_user, allowed_roles=["grantor", "supervisor"])
        if requirement.stage.completion_status != "active":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Stage is not active")
        if not requirement.proof_url:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Proof not submitted yet")
        requirement.status = "completed"

        await self.session.commit()
        await self.session.refresh(requirement)
        return RequirementRead.model_validate(requirement, from_attributes=True)

    async def submit_requirement_proof(
        self, requirement_id: str, payload: RequirementProofSubmit, current_user: User
    ) -> RequirementRead:
        requirement_uuid = self._parse_uuid(requirement_id)
        requirement = await self.repo.get_requirement(requirement_uuid)
        if not requirement:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Requirement not found")

        if requirement.description and str(requirement.description).startswith("payment_contract_id:"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Proof cannot be submitted for smart-contract enforced stages",
            )

        program = requirement.stage.grant_program
        self._ensure_role(program, current_user, allowed_roles=["grantee"])
        if program.status != "active" or requirement.stage.completion_status != "active":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Stage is not active")
        if requirement.status == "completed":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Requirement already completed")

        requirement.proof_url = payload.proof_url
        requirement.proof_submitted_by = current_user.id
        await self.session.commit()
        await self.session.refresh(requirement)
        return RequirementRead.model_validate(requirement, from_attributes=True)

    async def complete_stage(self, stage_id: str, current_user: User) -> StageRead:
        stage_uuid = self._parse_uuid(stage_id)
        stage = await self.repo.get_stage(stage_uuid)
        if not stage:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stage not found")

        program = stage.grant_program
        contract_requirement = any(
            req.description and str(req.description).startswith("payment_contract_id:") for req in stage.requirements
        )
        allowed_roles = ["grantor", "supervisor"] + (["grantee"] if contract_requirement else [])
        self._ensure_role(program, current_user, allowed_roles=allowed_roles)
        if program.status != "active":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Grant is not active")
        if stage.completion_status != "active":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Stage is not active")

        pending_reqs = [req for req in stage.requirements if req.status != "completed"]
        if pending_reqs and not contract_requirement:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot complete stage with pending requirements"
            )

        stage.completion_status = "completed"
        next_stage = self._get_next_stage(program, stage.order)
        if next_stage:
            next_stage.completion_status = "active"
        else:
            program.status = "completed"

        await self.session.commit()
        await self.session.refresh(stage)

        if not contract_requirement:
            await self.payment_service.send_stage_payout(stage)
        return StageRead.model_validate(stage, from_attributes=True)

    async def _ensure_user_exists(self, user_id: str) -> UUID:
        parsed_id = self._parse_uuid(user_id)
        exists = await self.user_repo.get_by_id(parsed_id)
        if not exists:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return parsed_id

    @staticmethod
    def _parse_uuid(user_id: str) -> UUID:
        try:
            return UUID(str(user_id))
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user id")

    def _ensure_role(self, program: GrantProgram, user: User, allowed_roles: list[str]) -> None:
        if program.grantor_id == user.id and "grantor" in allowed_roles:
            return
        participant_roles = [p.role for p in program.participants if str(p.user_id) == str(user.id) and p.active]
        if any(role in allowed_roles for role in participant_roles):
            return
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

    async def update_bank_account(
        self, grant_program_id: str, payload: GrantBankAccountUpdate, current_user: User
    ) -> GrantProgramRead:
        program_id = self._parse_uuid(grant_program_id)
        program = await self.repo.get(program_id)
        if not program:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grant not found")
        self._ensure_role(program, current_user, allowed_roles=["grantor"])
        program.bank_account_number = payload.bank_account_number
        await self.session.commit()
        await self.session.refresh(program)
        return GrantProgramRead.model_validate(program, from_attributes=True)

    async def _resolve_user_identifier(self, participant: GrantParticipantCreate) -> UUID:
        if participant.user_email:
            user = await self.user_repo.get_by_email(participant.user_email)
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
            return user.id
        if participant.user_id:
            return await self._ensure_user_exists(participant.user_id)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User identifier missing")

    @staticmethod
    def _get_next_stage(program: GrantProgram, current_order: int) -> Stage | None:
        ordered = sorted(program.stages, key=lambda s: s.order)
        for stage in ordered:
            if stage.order > current_order:
                return stage
        return None

    @staticmethod
    def _validate_stage_order(payload: GrantProgramCreate) -> None:
        orders = sorted(stage.order for stage in payload.stages)
        expected = list(range(1, len(orders) + 1))
        if orders != expected:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Stages must be sequential and start at 1",
            )
