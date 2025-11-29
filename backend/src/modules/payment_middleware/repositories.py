from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import PaymentContract


class PaymentContractRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, contract: PaymentContract) -> PaymentContract:
        self.session.add(contract)
        await self.session.commit()
        await self.session.refresh(contract)
        return contract

    async def list(self) -> List[PaymentContract]:
        result = await self.session.execute(select(PaymentContract).order_by(PaymentContract.created_at.desc()))
        return list(result.scalars().all())

    async def get(self, contract_id: UUID) -> Optional[PaymentContract]:
        result = await self.session.execute(select(PaymentContract).where(PaymentContract.id == contract_id))
        return result.scalar_one_or_none()

    async def delete(self, contract: PaymentContract) -> None:
        await self.session.delete(contract)
        await self.session.commit()
