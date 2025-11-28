import httpx

from src.core.config import settings


class SimplePaymentGateway:
    def __init__(self) -> None:
        self.base_url = settings.mir_api_base_url.rstrip("/")
        self.api_key = settings.mir_api_key

    async def identify_participant(self, participant_id: str) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/participants/{participant_id}", headers=self._headers(), timeout=30.0
            )
            response.raise_for_status()
            return response.json()

    async def send_payment(self, participant_id: str, amount: float, reference: str) -> dict:
        payload = {"participant_id": participant_id, "amount": amount, "reference": reference}
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/payments", headers=self._headers(), json=payload, timeout=30.0)
            response.raise_for_status()
            return response.json()

    async def poll_transaction(self, transaction_id: str) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/payments/{transaction_id}", headers=self._headers(), timeout=30.0
            )
            response.raise_for_status()
            return response.json()

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
