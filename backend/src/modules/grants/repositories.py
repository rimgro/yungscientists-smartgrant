from typing import Optional

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .models import GrantProgram, Requirement, Stage, UserToGrant


class GrantRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, grant_program_id: str) -> Optional[GrantProgram]:
        result = await self.session.execute(
            select(GrantProgram)
            .where(GrantProgram.id == grant_program_id)
            .options(
                selectinload(GrantProgram.stages).selectinload(Stage.requirements),
                selectinload(GrantProgram.participants).selectinload(UserToGrant.user),
            )
        )
        return result.scalar_one_or_none()

    async def create(self, program: GrantProgram) -> GrantProgram:
        self.session.add(program)
        await self.session.flush()
        return program

    async def list_for_user(self, user_id: str) -> list[GrantProgram]:
        stmt = (
            select(GrantProgram)
            .outerjoin(UserToGrant, UserToGrant.grant_program_id == GrantProgram.id)
            .where(or_(GrantProgram.grantor_id == user_id, UserToGrant.user_id == user_id))
            .options(
                selectinload(GrantProgram.stages).selectinload(Stage.requirements),
                selectinload(GrantProgram.participants).selectinload(UserToGrant.user),
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

    async def get_stage(self, stage_id: str) -> Optional[Stage]:
        result = await self.session.execute(
            select(Stage)
                .where(Stage.id == stage_id)
                .options(
                    selectinload(Stage.requirements),
                    selectinload(Stage.grant_program).selectinload(GrantProgram.stages),
                    selectinload(Stage.grant_program).selectinload(GrantProgram.participants).selectinload(UserToGrant.user),
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
                .selectinload(GrantProgram.participants)
                .selectinload(UserToGrant.user),
                selectinload(Requirement.stage).selectinload(Stage.grant_program).selectinload(GrantProgram.stages),
                selectinload(Requirement.stage),
            )
        )
        return result.scalar_one_or_none()
