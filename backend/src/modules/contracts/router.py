from fastapi import APIRouter

from .services import ContractService

router = APIRouter(prefix="/contracts", tags=["contracts"])
service = ContractService()


@router.post("/{grant_program_id}/execute")
async def trigger_contract(grant_program_id: str) -> dict:
    return await service.trigger_contract_action(grant_program_id)
