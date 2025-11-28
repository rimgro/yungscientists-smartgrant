import requests
import logging
from typing import List
from models import DepositRequest, TransferRequest, TransactionResponse, BalanceResponse

class BankAPIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.logger = logging.getLogger(__name__)

    def deposit(self, request: DepositRequest) -> TransactionResponse:
        """Пополнение счета через API банка"""
        try:
            response = requests.post(
                f"{self.base_url}/deposit",
                json=request.dict()
            )
            response.raise_for_status()
            return TransactionResponse(**response.json())
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Deposit API error: {e}")
            raise Exception(f"Bank API error: {str(e)}")

    def transfer(self, request: TransferRequest) -> TransactionResponse:
        """Перевод денег через API банка"""
        try:
            response = requests.post(
                f"{self.base_url}/transfer",
                json=request.dict()
            )
            response.raise_for_status()
            return TransactionResponse(**response.json())
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Transfer API error: {e}")
            raise Exception(f"Bank API error: {str(e)}")

    def get_balance(self, card_number: str) -> BalanceResponse:
        """Получение баланса через API банка"""
        try:
            response = requests.get(
                f"{self.base_url}/balance/{card_number}"
            )
            response.raise_for_status()
            return BalanceResponse(**response.json())
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Balance API error: {e}")
            raise Exception(f"Bank API error: {str(e)}")

    def get_transactions(self, card_number: str) -> List[TransactionResponse]:
        """История транзакций через API банка"""
        try:
            response = requests.get(
                f"{self.base_url}/transactions/{card_number}"
            )
            response.raise_for_status()
            transactions_data = response.json()
            return [TransactionResponse(**tx) for tx in transactions_data]
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Transactions API error: {e}")
            raise Exception(f"Bank API error: {str(e)}")