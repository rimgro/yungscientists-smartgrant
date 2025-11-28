from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import GrantProgram, Stage


class GrantRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, grant_program_id: str) -> Optional[GrantProgram]:
        result = await self.session.execute(
            select(GrantProgram).where(GrantProgram.id == grant_program_id).options()
        )
        return result.scalar_one_or_none()

    async def create(self, program: GrantProgram) -> GrantProgram:
        self.session.add(program)
        await self.session.flush()
        return program

    async def list(self) -> list[GrantProgram]:
        result = await self.session.execute(select(GrantProgram))
        return list(result.scalars().unique().all())

    async def get_stage(self, stage_id: str) -> Optional[Stage]:
        result = await self.session.execute(select(Stage).where(Stage.id == stage_id))
        return result.scalar_one_or_none()
