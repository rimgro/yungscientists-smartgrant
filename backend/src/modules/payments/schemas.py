from pydantic import BaseModel, Field


class PaymentCreate(BaseModel):
    participant_id: str
    amount: float = Field(..., gt=0)
    reference: str


class PaymentStatus(BaseModel):
    transaction_id: str
    status: str
