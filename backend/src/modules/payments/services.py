from src.modules.grants.models import Stage
from .gateway import SimplePaymentGateway
from .schemas import PaymentCreate, PaymentStatus


class PaymentService:
    def __init__(self) -> None:
        self.gateway = SimplePaymentGateway()

    async def send_payment(self, payload: PaymentCreate) -> PaymentStatus:
        response = await self.gateway.send_payment(
            participant_id=payload.participant_id, amount=payload.amount, reference=payload.reference
        )
        return PaymentStatus(transaction_id=response.get("transaction_id", ""), status=response.get("status", "unknown"))

    async def poll_status(self, transaction_id: str) -> PaymentStatus:
        response = await self.gateway.poll_transaction(transaction_id)
        return PaymentStatus(transaction_id=transaction_id, status=response.get("status", "unknown"))

    async def send_stage_payout(self, stage: Stage) -> None:
        await self.gateway.send_payment(
            participant_id=str(stage.grant_program.bank_account_number),
            amount=float(stage.amount),
            reference=f"GrantStage:{stage.id}",
        )

    async def deposit_grant(self, *, participant_id: str, amount: float) -> PaymentStatus:
        """
        Stubbed deposit used on grant confirmation. Assumes funds are deposited successfully.
        This will be replaced with a real gateway call later.
        """
        return PaymentStatus(transaction_id="local-deposit", status="deposited")
