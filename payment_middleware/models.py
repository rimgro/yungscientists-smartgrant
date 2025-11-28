from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime

class TransactionType(str, Enum):
    DEPOSIT = "deposit"
    TRANSFER = "transfer"
    PAYMENT = "payment"

class PurchaseInfo(BaseModel):
    mcc: str = Field(..., description="Merchant Category Code")
    cost: float = Field(..., description="Стоимость покупки")
    merchant_id: str = Field(..., description="ID мерчанта")
    card_number: str = Field(..., description="Номер карты")

class DepositRequest(BaseModel):
    card_number: str = Field(..., description="Номер карты")
    amount: float = Field(..., description="Сумма пополнения")

class TransferRequest(BaseModel):
    from_card: str = Field(..., description="Карта отправителя")
    to_card: str = Field(..., description="Карта получателя")
    amount: float = Field(..., description="Сумма перевода")

class TransactionResponse(BaseModel):
    transaction_id: str
    status: str
    amount: float
    type: TransactionType
    timestamp: str

class BalanceResponse(BaseModel):
    card_number: str
    balance: float
    currency: str = "RUB"

class RuleCheckResponse(BaseModel):
    allowed: bool
    reason: Optional[str] = None
    rules_checked: List[str]
    details: Optional[Dict[str, Any]] = None

class ContractCreateRequest(BaseModel):
    name: str = Field(..., description="Название контракта")
    contract_type: str = Field(..., description="Тип контракта: mcc_limit, merchant_block, amount_limit, time_restriction, card_restriction")
    parameters: Dict[str, Any] = Field(..., description="Параметры контракта")
    description: Optional[str] = Field(None, description="Описание контракта")

class ContractResponse(BaseModel):
    contract_id: str
    name: str
    contract_type: str
    parameters: Dict[str, Any]
    description: Optional[str]
    status: str
    created_at: str

class ContractExecutionRequest(BaseModel):
    contract_id: str
    purchase_info: PurchaseInfo

class ContractExecutionResponse(BaseModel):
    allowed: bool
    reason: Optional[str] = None
    contract_id: str
    contract_name: str
    details: Optional[Dict[str, Any]] = None