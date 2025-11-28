from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class TransactionType(str, Enum):
    DEPOSIT = "deposit"
    TRANSFER = "transfer"

class DepositRequest(BaseModel):
    amount: float = Field(gt=0, description="Сумма пополнения")
    card_number: str = Field(..., description="Номер карты для пополнения")

class TransferRequest(BaseModel):
    amount: float = Field(gt=0, description="Сумма перевода")
    from_card: str = Field(..., description="Карта отправителя")
    to_card: str = Field(..., description="Карта получателя")
    description: Optional[str] = Field(None, description="Описание перевода")

class TransactionResponse(BaseModel):
    transaction_id: str
    type: TransactionType
    amount: float
    card_number: str
    timestamp: datetime
    status: str
    message: str

class AccountBalance(BaseModel):
    card_number: str
    balance: float
    currency: str = "RUB"