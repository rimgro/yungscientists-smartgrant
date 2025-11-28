from fastapi import APIRouter, Depends

from .schemas import PaymentCreate, PaymentStatus
from .services import PaymentService

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/", response_model=PaymentStatus)
async def send_payment(payload: PaymentCreate, service: PaymentService = Depends(PaymentService)) -> PaymentStatus:
    return await service.send_payment(payload)


@router.get("/{transaction_id}", response_model=PaymentStatus)
async def poll_transaction(transaction_id: str, service: PaymentService = Depends(PaymentService)) -> PaymentStatus:
    return await service.poll_status(transaction_id)
