from typing import List

from fastapi import APIRouter, Depends, status

from src.core.database import get_session
from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import (
    BalanceResponse,
    CardContractsResponse,
    ContractCreate,
    ContractExecutionRequest,
    ContractExecutionResponse,
    ContractRead,
    DepositRequest,
    PurchaseInfo,
    RuleCheckResponse,
    TransactionResponse,
    TransferRequest,
)
from .services import PaymentMiddlewareService

router = APIRouter(prefix="/payment-middleware", tags=["payment-middleware"])


async def get_service(session: AsyncSession = Depends(get_session)) -> PaymentMiddlewareService:
    return PaymentMiddlewareService(session)


@router.get("/health")
async def health(service: PaymentMiddlewareService = Depends(get_service)) -> dict[str, str]:
    return await service.health()


@router.post("/contracts", response_model=ContractRead)
async def create_contract(
    payload: ContractCreate, service: PaymentMiddlewareService = Depends(get_service)
) -> ContractRead:
    return await service.create_contract(payload)


@router.get("/contracts", response_model=List[ContractRead])
async def list_contracts(service: PaymentMiddlewareService = Depends(get_service)) -> List[ContractRead]:
    return await service.list_contracts()


@router.post("/contracts/execute", response_model=ContractExecutionResponse)
async def execute_contract(
    payload: ContractExecutionRequest, service: PaymentMiddlewareService = Depends(get_service)
) -> ContractExecutionResponse:
    return await service.execute_contract(payload)


@router.delete("/contracts/{contract_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contract(contract_id: str, service: PaymentMiddlewareService = Depends(get_service)) -> None:
    await service.delete_contract(contract_id)


@router.get("/cards/{card_number}/contracts", response_model=CardContractsResponse)
async def card_contracts(
    card_number: str, service: PaymentMiddlewareService = Depends(get_service)
) -> CardContractsResponse:
    return await service.get_contracts_for_card(card_number)


@router.post("/check-purchase", response_model=RuleCheckResponse)
async def check_purchase(
    purchase_info: PurchaseInfo, service: PaymentMiddlewareService = Depends(get_service)
) -> RuleCheckResponse:
    return await service.check_purchase(purchase_info)


@router.post("/process-purchase", response_model=TransactionResponse)
async def process_purchase(
    purchase_info: PurchaseInfo, service: PaymentMiddlewareService = Depends(get_service)
) -> TransactionResponse:
    return await service.process_purchase(purchase_info)


@router.post("/process-purchase-with-contract", response_model=TransactionResponse)
async def process_purchase_with_contract(
    contract_id: str, purchase_info: PurchaseInfo, service: PaymentMiddlewareService = Depends(get_service)
) -> TransactionResponse:
    return await service.process_purchase_with_contract(contract_id, purchase_info)


@router.post("/deposit", response_model=TransactionResponse)
async def deposit(
    payload: DepositRequest, service: PaymentMiddlewareService = Depends(get_service)
) -> TransactionResponse:
    return await service.deposit(payload)


@router.post("/transfer", response_model=TransactionResponse)
async def transfer(
    payload: TransferRequest, service: PaymentMiddlewareService = Depends(get_service)
) -> TransactionResponse:
    return await service.transfer(payload)


@router.get("/balance/{card_number}", response_model=BalanceResponse)
async def balance(card_number: str, service: PaymentMiddlewareService = Depends(get_service)) -> BalanceResponse:
    return await service.balance(card_number)


@router.get("/transactions/{card_number}", response_model=List[TransactionResponse])
async def transactions(
    card_number: str, service: PaymentMiddlewareService = Depends(get_service)
) -> List[TransactionResponse]:
    return await service.transactions(card_number)


@router.get("/rules/mcc")
async def mcc_rules() -> dict[str, int]:
    # Stubbed MCC rules map kept minimal for UI/reference.
    return {"5411": 20000, "5812": 15000}
