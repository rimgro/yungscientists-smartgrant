import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from .models import PaymentContract
from .repositories import PaymentContractRepository
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
    TransactionType,
    TransferRequest,
)


shared_bank_client = None


class BankAPIClient:
    """
    Adapter around an external bank API. Falls back to an in-memory ledger
    when PAYMENT_BANK_API_BASE_URL is not configured.
    """

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url.rstrip("/") if base_url else None
        self._balances: dict[str, float] = {
            "1234567812345678": 50_000.0,
            "8765432187654321": 100_000.0,
            "1111222233334444": 15_000.0,
        }
        self._transactions: dict[str, list[TransactionResponse]] = {}

    async def health(self) -> dict[str, str]:
        if not self.base_url:
            return {"status": "healthy", "service": "smart-contract-bank-service", "bank_api": "stub"}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/health", timeout=10.0)
                response.raise_for_status()
                payload = response.json()
            return {
                "status": payload.get("status", "healthy"),
                "service": payload.get("service", "smart-contract-bank-service"),
                "bank_api": "available",
            }
        except Exception as exc:  # pragma: no cover - network failures are covered by stub
            return {"status": "degraded", "bank_api": "unavailable", "error": str(exc)}

    async def deposit(self, request: DepositRequest) -> TransactionResponse:
        if self.base_url:
            return await self._post_transaction("/deposit", request.model_dump())
        return self._apply_balance_change(
            card_number=request.card_number, delta=request.amount, tx_type=TransactionType.deposit
        )

    async def transfer(self, request: TransferRequest) -> TransactionResponse:
        if self.base_url:
            return await self._post_transaction("/transfer", request.model_dump())
        if self._get_balance(request.from_card) < request.amount:
            raise ValueError("Insufficient funds")
        self._apply_balance_change(card_number=request.from_card, delta=-request.amount, tx_type=TransactionType.transfer)
        return self._apply_balance_change(
            card_number=request.to_card, delta=request.amount, tx_type=TransactionType.transfer
        )

    async def payment(self, purchase_info: PurchaseInfo) -> TransactionResponse:
        if self.base_url:
            payload = {"from_card": purchase_info.card_number, "to_card": f"MERCHANT_{purchase_info.merchant_id}"}
            payload.update({"amount": purchase_info.cost})
            return await self._post_transaction("/transfer", payload)
        if self._get_balance(purchase_info.card_number) < purchase_info.cost:
            raise ValueError("Insufficient funds")
        self._apply_balance_change(
            card_number=purchase_info.card_number, delta=-purchase_info.cost, tx_type=TransactionType.payment
        )
        return self._apply_balance_change(
            card_number=f"MERCHANT_{purchase_info.merchant_id}",
            delta=purchase_info.cost,
            tx_type=TransactionType.payment,
        )

    async def get_balance(self, card_number: str) -> BalanceResponse:
        if self.base_url:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/balance/{card_number}", timeout=10.0)
                response.raise_for_status()
                payload = response.json()
            return BalanceResponse(**payload)
        return BalanceResponse(card_number=card_number, balance=self._get_balance(card_number), currency="RUB")

    async def get_transactions(self, card_number: str) -> List[TransactionResponse]:
        if self.base_url:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/transactions/{card_number}", timeout=10.0)
                response.raise_for_status()
                data = response.json()
            return [TransactionResponse(**item) for item in data]
        return list(self._transactions.get(card_number, []))

    def _get_balance(self, card_number: str) -> float:
        return float(self._balances.get(card_number, 0.0))

    def _apply_balance_change(self, *, card_number: str, delta: float, tx_type: TransactionType) -> TransactionResponse:
        new_balance = self._get_balance(card_number) + delta
        self._balances[card_number] = new_balance
        transaction = TransactionResponse(
            transaction_id=str(uuid.uuid4()),
            status="completed",
            amount=abs(delta),
            type=tx_type,
            timestamp=datetime.utcnow().isoformat(),
        )
        self._transactions.setdefault(card_number, []).append(transaction)
        return transaction

    async def _post_transaction(self, path: str, payload: dict[str, Any]) -> TransactionResponse:
        assert self.base_url  # for mypy
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}{path}", json=payload, timeout=15.0)
            response.raise_for_status()
            return TransactionResponse(**response.json())


class RulesEngine:
    """Minimal rules from the payment middleware docs."""

    def check_purchase(self, purchase_info: PurchaseInfo) -> RuleCheckResponse:
        rules_checked = []
        details: dict[str, Any] = {}
        amount_ok = self._check_amount(purchase_info.cost, details)
        rules_checked.append("Amount validation")
        allowed = amount_ok
        reason = None if allowed else details.get("amount_check", "Basic validation failed")
        return RuleCheckResponse(allowed=allowed, reason=reason, rules_checked=rules_checked, details=details)

    @staticmethod
    def _check_amount(cost: float, details: dict[str, Any]) -> bool:
        if cost <= 0:
            details["amount_check"] = "Amount must be positive"
            return False
        if cost > 1_000_000:
            details["amount_check"] = f"Amount {cost} exceeds maximum limit"
            return False
        details["amount_check"] = f"Amount {cost} is valid"
        return True


class PaymentMiddlewareService:
    def __init__(self, session: AsyncSession, bank_client: Optional[BankAPIClient] = None):
        self.repo = PaymentContractRepository(session)
        global shared_bank_client
        if shared_bank_client is None:
            shared_bank_client = BankAPIClient(settings.payment_bank_api_base_url)
        self.bank_client = bank_client or shared_bank_client
        self.rules_engine = RulesEngine()

    async def health(self) -> dict[str, str]:
        result = await self.bank_client.health()
        return {"status": result.get("status", "healthy"), "service": "smart-contract-bank-service", **result}

    async def create_contract(self, payload: ContractCreate) -> ContractRead:
        parameters = dict(payload.parameters)
        self._validate_contract_parameters(payload.contract_type, parameters)
        contract = PaymentContract(
            name=payload.name,
            contract_type=payload.contract_type,
            parameters=parameters,
            description=payload.description,
            status="active",
        )
        saved = await self.repo.create(contract)
        return self._to_contract_read(saved)

    async def list_contracts(self) -> List[ContractRead]:
        contracts = await self.repo.list()
        return [self._to_contract_read(c) for c in contracts]

    async def execute_contract(self, payload: ContractExecutionRequest) -> ContractExecutionResponse:
        contract = await self._get_contract_or_404(payload.contract_id)
        applicability = self._check_card_applicability(contract.parameters, payload.purchase_info.card_number)
        if not applicability["applicable"]:
            return ContractExecutionResponse(
                allowed=True,
                reason=applicability.get("reason"),
                contract_id=str(contract.id),
                contract_name=contract.name,
                details={"card_applicability": applicability},
            )

        result = self._execute_contract_logic(contract.contract_type, contract.parameters, payload.purchase_info)
        return ContractExecutionResponse(
            allowed=bool(result["allowed"]),
            reason=result.get("reason"),
            contract_id=str(contract.id),
            contract_name=contract.name,
            details=result.get("details"),
        )

    async def delete_contract(self, contract_id: str) -> None:
        contract = await self._get_contract_or_404(contract_id)
        await self.repo.delete(contract)

    async def get_contracts_for_card(self, card_number: str) -> CardContractsResponse:
        contracts = await self.repo.list()
        applicable = [
            contract
            for contract in contracts
            if self._check_card_applicability(contract.parameters, card_number)["applicable"]
            and contract.status == "active"
        ]
        return CardContractsResponse(
            card_number=card_number,
            applicable_contracts_count=len(applicable),
            contracts=[self._to_contract_read(c) for c in applicable],
        )

    async def check_purchase(self, purchase_info: PurchaseInfo) -> RuleCheckResponse:
        return self.rules_engine.check_purchase(purchase_info)

    async def process_purchase(self, purchase_info: PurchaseInfo) -> TransactionResponse:
        rules = self.rules_engine.check_purchase(purchase_info)
        if not rules.allowed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"Transaction not allowed: {rules.reason}"
            )
        balance = await self.bank_client.get_balance(purchase_info.card_number)
        if balance.balance < purchase_info.cost:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient funds. Balance: {balance.balance}, Required: {purchase_info.cost}",
            )
        return await self.bank_client.payment(purchase_info)

    async def process_purchase_with_contract(self, contract_id: str, purchase_info: PurchaseInfo) -> TransactionResponse:
        rules = self.rules_engine.check_purchase(purchase_info)
        if not rules.allowed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"Basic validation failed: {rules.reason}"
            )

        contract = await self._get_contract_or_404(contract_id)
        execution = self._execute_contract_logic(contract.contract_type, contract.parameters, purchase_info)
        if not execution["allowed"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Contract violation: {execution.get('reason')}",
            )
        balance = await self.bank_client.get_balance(purchase_info.card_number)
        if balance.balance < purchase_info.cost:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient funds. Balance: {balance.balance}, Required: {purchase_info.cost}",
            )
        return await self.bank_client.payment(purchase_info)

    async def deposit(self, request: DepositRequest) -> TransactionResponse:
        return await self.bank_client.deposit(request)

    async def transfer(self, request: TransferRequest) -> TransactionResponse:
        return await self.bank_client.transfer(request)

    async def balance(self, card_number: str) -> BalanceResponse:
        return await self.bank_client.get_balance(card_number)

    async def transactions(self, card_number: str) -> List[TransactionResponse]:
        return await self.bank_client.get_transactions(card_number)

    async def _get_contract_or_404(self, contract_id: str) -> PaymentContract:
        try:
            parsed_id = uuid.UUID(str(contract_id))
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid contract id")

        contract = await self.repo.get(parsed_id)
        if not contract:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found")
        return contract

    def _validate_contract_parameters(self, contract_type: str, parameters: Dict[str, Any]) -> None:
        if "applicable_cards" not in parameters:
            parameters["applicable_cards"] = ["all"]
        elif not isinstance(parameters["applicable_cards"], list):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="applicable_cards must be a list")

        if contract_type == "mcc_limit":
            allowed = parameters.get("allowed_mcc")
            if allowed is None or not isinstance(allowed, list):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="MCC limit contract requires 'allowed_mcc' list"
                )
            blocked = parameters.get("blocked_mcc")
            if blocked is None:
                parameters["blocked_mcc"] = []
        elif contract_type == "merchant_block":
            blocked_merchants = parameters.get("blocked_merchants")
            if blocked_merchants is None or not isinstance(blocked_merchants, list):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Merchant block contract requires 'blocked_merchants'"
                )
        elif contract_type == "amount_limit":
            max_amount = parameters.get("max_amount")
            if max_amount is None or not isinstance(max_amount, (int, float)):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Amount limit contract requires 'max_amount' number"
                )
        elif contract_type == "time_restriction":
            restricted_hours = parameters.get("restricted_hours")
            if restricted_hours is None or not isinstance(restricted_hours, list):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Time restriction contract requires 'restricted_hours'"
                )
            for hour in restricted_hours:
                if not isinstance(hour, int) or hour < 0 or hour > 23:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Restricted hours must be integers between 0 and 23",
                    )
        elif contract_type == "card_restriction":
            allowed_cards = parameters.get("allowed_cards")
            if allowed_cards is None or not isinstance(allowed_cards, list):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Card restriction contract requires 'allowed_cards'"
                )
            blocked_cards = parameters.get("blocked_cards")
            if blocked_cards is None:
                parameters["blocked_cards"] = []
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unknown contract type: {contract_type}")

    def _check_card_applicability(self, parameters: Dict[str, Any], card_number: str) -> Dict[str, Any]:
        applicable_cards = parameters.get("applicable_cards", ["all"])
        if "all" in applicable_cards or card_number in applicable_cards:
            return {"applicable": True, "reason": "Contract applies to card"}
        return {
            "applicable": False,
            "reason": f"Card {card_number} not in applicable cards list",
            "details": {"applicable_cards": applicable_cards},
        }

    def _execute_contract_logic(self, contract_type: str, parameters: Dict[str, Any], purchase_info: PurchaseInfo) -> Dict[str, Any]:
        if contract_type == "mcc_limit":
            return self._execute_mcc_limit(parameters, purchase_info)
        if contract_type == "merchant_block":
            return self._execute_merchant_block(parameters, purchase_info)
        if contract_type == "amount_limit":
            return self._execute_amount_limit(parameters, purchase_info)
        if contract_type == "time_restriction":
            return self._execute_time_restriction(parameters)
        if contract_type == "card_restriction":
            return self._execute_card_restriction(parameters, purchase_info)
        return {"allowed": False, "reason": f"Unknown contract type: {contract_type}"}

    @staticmethod
    def _execute_mcc_limit(parameters: Dict[str, Any], purchase_info: PurchaseInfo) -> Dict[str, Any]:
        allowed_mcc = parameters.get("allowed_mcc", [])
        blocked_mcc = parameters.get("blocked_mcc", [])
        if allowed_mcc and purchase_info.mcc not in allowed_mcc:
            return {
                "allowed": False,
                "reason": f"MCC {purchase_info.mcc} not in allowed list",
                "details": {"allowed_mcc": allowed_mcc, "current_mcc": purchase_info.mcc},
            }
        if purchase_info.mcc in blocked_mcc:
            return {
                "allowed": False,
                "reason": f"MCC {purchase_info.mcc} is blocked",
                "details": {"blocked_mcc": blocked_mcc, "current_mcc": purchase_info.mcc},
            }
        return {"allowed": True, "reason": "MCC check passed"}

    @staticmethod
    def _execute_merchant_block(parameters: Dict[str, Any], purchase_info: PurchaseInfo) -> Dict[str, Any]:
        blocked_merchants = parameters.get("blocked_merchants", [])
        if purchase_info.merchant_id in blocked_merchants:
            return {
                "allowed": False,
                "reason": f"Merchant {purchase_info.merchant_id} is blocked",
                "details": {"blocked_merchants": blocked_merchants, "current_merchant": purchase_info.merchant_id},
            }
        return {"allowed": True, "reason": "Merchant check passed"}

    @staticmethod
    def _execute_amount_limit(parameters: Dict[str, Any], purchase_info: PurchaseInfo) -> Dict[str, Any]:
        max_amount = parameters.get("max_amount", float("inf"))
        if purchase_info.cost > max_amount:
            return {
                "allowed": False,
                "reason": f"Amount {purchase_info.cost} exceeds limit {max_amount}",
                "details": {"max_amount": max_amount, "current_amount": purchase_info.cost},
            }
        return {"allowed": True, "reason": "Amount check passed"}

    @staticmethod
    def _execute_time_restriction(parameters: Dict[str, Any]) -> Dict[str, Any]:
        restricted_hours = parameters.get("restricted_hours", [])
        current_hour = datetime.now().hour
        if current_hour in restricted_hours:
            return {
                "allowed": False,
                "reason": f"Transactions not allowed at hour {current_hour}:00",
                "details": {"restricted_hours": restricted_hours, "current_hour": current_hour},
            }
        return {"allowed": True, "reason": "Time check passed"}

    @staticmethod
    def _execute_card_restriction(parameters: Dict[str, Any], purchase_info: PurchaseInfo) -> Dict[str, Any]:
        allowed_cards = parameters.get("allowed_cards", [])
        blocked_cards = parameters.get("blocked_cards", [])
        if allowed_cards and purchase_info.card_number not in allowed_cards:
            return {
                "allowed": False,
                "reason": f"Card {purchase_info.card_number} not in allowed list",
                "details": {"allowed_cards": allowed_cards, "current_card": purchase_info.card_number},
            }
        if purchase_info.card_number in blocked_cards:
            return {
                "allowed": False,
                "reason": f"Card {purchase_info.card_number} is blocked",
                "details": {"blocked_cards": blocked_cards, "current_card": purchase_info.card_number},
            }
        return {"allowed": True, "reason": "Card check passed"}

    @staticmethod
    def _to_contract_read(contract: PaymentContract) -> ContractRead:
        return ContractRead(
            contract_id=str(contract.id),
            name=contract.name,
            contract_type=contract.contract_type,
            parameters=contract.parameters,
            description=contract.description,
            status=contract.status,
            created_at=contract.created_at,
        )
