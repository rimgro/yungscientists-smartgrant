from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.payments.services import PaymentService
from .models import GrantProgram, Requirement, Stage
from .repositories import GrantRepository
from .schemas import GrantProgramCreate, GrantProgramRead, StageRead


class GrantService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = GrantRepository(session)
        self.payment_service = PaymentService()

    async def create_program(self, payload: GrantProgramCreate) -> GrantProgramRead:
        self._validate_stage_order(payload)

        program = GrantProgram(name=payload.name, grant_receiver=payload.grant_receiver)
        for stage_payload in sorted(payload.stages, key=lambda s: s.order):
            stage = Stage(order=stage_payload.order, amount=stage_payload.amount)
            for req_payload in stage_payload.requirements:
                requirement = Requirement(name=req_payload.name, description=req_payload.description)
                stage.requirements.append(requirement)
            program.stages.append(stage)

        await self.repo.create(program)
        await self.session.commit()
        await self.session.refresh(program)
        return GrantProgramRead.model_validate(program)

    async def list_programs(self) -> list[GrantProgramRead]:
        programs = await self.repo.list()
        return [GrantProgramRead.model_validate(p) for p in programs]

    async def complete_stage(self, stage_id: str) -> StageRead:
        stage = await self.repo.get_stage(stage_id)
        if not stage:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stage not found")

        pending_reqs = [req for req in stage.requirements if req.status != "completed"]
        if pending_reqs:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot complete stage with pending requirements"
            )

        stage.completion_status = "completed"
        await self.session.commit()
        await self.session.refresh(stage)

        await self.payment_service.send_stage_payout(stage)
        return StageRead.model_validate(stage)

    @staticmethod
    def _validate_stage_order(payload: GrantProgramCreate) -> None:
        orders = sorted(stage.order for stage in payload.stages)
        expected = list(range(1, len(orders) + 1))
        if orders != expected:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Stages must be sequential and start at 1",
            )
