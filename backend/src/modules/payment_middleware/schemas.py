from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class TransactionType(str, Enum):
    deposit = "deposit"
    transfer = "transfer"
    payment = "payment"


class PurchaseInfo(BaseModel):
    mcc: str = Field(..., description="Merchant Category Code")
    cost: float = Field(..., gt=0, description="Стоимость покупки")
    merchant_id: str = Field(..., description="ID мерчанта")
    card_number: str = Field(..., description="Номер карты")


class DepositRequest(BaseModel):
    card_number: str = Field(..., description="Номер карты")
    amount: float = Field(..., gt=0, description="Сумма пополнения")


class TransferRequest(BaseModel):
    from_card: str = Field(..., description="Карта отправителя")
    to_card: str = Field(..., description="Карта получателя")
    amount: float = Field(..., gt=0, description="Сумма перевода")


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


class ContractCreate(BaseModel):
    name: str = Field(..., description="Название контракта")
    contract_type: str = Field(
        ...,
        description="Тип контракта: mcc_limit, merchant_block, amount_limit, time_restriction, card_restriction",
    )
    parameters: Dict[str, Any] = Field(..., description="Параметры контракта")
    description: Optional[str] = Field(None, description="Описание контракта")


class ContractRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    contract_id: str
    name: str
    contract_type: str
    parameters: Dict[str, Any]
    description: Optional[str]
    status: str
    created_at: datetime


class ContractExecutionRequest(BaseModel):
    contract_id: str
    purchase_info: PurchaseInfo


class ContractExecutionResponse(BaseModel):
    allowed: bool
    reason: Optional[str] = None
    contract_id: str
    contract_name: str
    details: Optional[Dict[str, Any]] = None


class CardContractsResponse(BaseModel):
    card_number: str
    applicable_contracts_count: int
    contracts: List[ContractRead]
