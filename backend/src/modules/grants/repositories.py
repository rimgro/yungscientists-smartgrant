from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .models import GrantProgram, Requirement, Stage


class GrantRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, grant_program_id: str) -> Optional[GrantProgram]:
        result = await self.session.execute(
            select(GrantProgram)
            .where(GrantProgram.id == grant_program_id)
            .options(
                selectinload(GrantProgram.stages).selectinload(Stage.requirements),
                selectinload(GrantProgram.participants),
            )
        )
        return result.scalar_one_or_none()

    async def create(self, program: GrantProgram) -> GrantProgram:
        self.session.add(program)
        await self.session.flush()
        return program

    async def list(self) -> list[GrantProgram]:
        result = await self.session.execute(
            select(GrantProgram).options(
                selectinload(GrantProgram.stages).selectinload(Stage.requirements),
                selectinload(GrantProgram.participants),
            )
        )
        return list(result.scalars().unique().all())

    async def get_stage(self, stage_id: str) -> Optional[Stage]:
        result = await self.session.execute(
            select(Stage)
                .where(Stage.id == stage_id)
                .options(
                    selectinload(Stage.requirements),
                    selectinload(Stage.grant_program).selectinload(GrantProgram.stages),
                    selectinload(Stage.grant_program).selectinload(GrantProgram.participants),
                )
        )
        return result.scalar_one_or_none()

    async def get_requirement(self, requirement_id: str) -> Optional[Requirement]:
        result = await self.session.execute(
            select(Requirement)
            .where(Requirement.id == requirement_id)
            .options(
                selectinload(Requirement.stage)
                .selectinload(Stage.grant_program)
                .selectinload(GrantProgram.participants),
                selectinload(Requirement.stage).selectinload(Stage.grant_program).selectinload(GrantProgram.stages),
                selectinload(Requirement.stage),
            )
        )
        return result.scalar_one_or_none()
