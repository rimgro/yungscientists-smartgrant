from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
from typing import List

from models import (
    PurchaseInfo, DepositRequest, TransferRequest, 
    TransactionResponse, BalanceResponse, RuleCheckResponse,
    ContractCreateRequest, ContractResponse, ContractExecutionRequest,
    ContractExecutionResponse
)
from bank_client import BankAPIClient
from rules_engine import RulesEngine
from contract_manager import ContractManager

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Smart Contract Bank Service",
    description="Сервис для обработки покупок с шаблонными смарт-контрактами",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Конфигурация
BANK_API_URL = "http://localhost:8000"

# Инициализация клиентов
bank_client = BankAPIClient(BANK_API_URL)
rules_engine = RulesEngine()
contract_manager = ContractManager()

# Эндпоинты для смарт-контрактов
@app.post("/contracts", response_model=ContractResponse)
async def create_contract(request: ContractCreateRequest):
    """
    Создать новый смарт-контракт
    
    Доступные типы контрактов:
    - mcc_limit: ограничение по MCC кодам
      Параметры: {"allowed_mcc": ["5411", "5812"], "blocked_mcc": ["4121"]}
    
    - merchant_block: блокировка мерчантов
      Параметры: {"blocked_merchants": ["merchant_001", "merchant_002"]}
    
    - amount_limit: ограничение по сумме
      Параметры: {"max_amount": 5000}
    
    - time_restriction: ограничение по времени
      Параметры: {"restricted_hours": [23, 0, 1, 2, 3, 4, 5]}
    """
    try:
        return await contract_manager.create_contract(request)
    except Exception as e:
        logger.error(f"Contract creation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/contracts", response_model=List[ContractResponse])
async def list_contracts():
    """
    Получить список всех смарт-контрактов
    """
    try:
        return await contract_manager.list_contracts()
    except Exception as e:
        logger.error(f"Contract listing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/contracts/execute", response_model=ContractExecutionResponse)
async def execute_contract(request: ContractExecutionRequest):
    """
    Выполнить смарт-контракт для проверки покупки
    """
    try:
        return await contract_manager.execute_contract(
            request.contract_id, 
            request.purchase_info
        )
    except Exception as e:
        logger.error(f"Contract execution failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/contracts/{contract_id}")
async def delete_contract(contract_id: str):
    """
    Удалить смарт-контракт
    """
    try:
        success = await contract_manager.delete_contract(contract_id)
        if success:
            return {"message": f"Contract {contract_id} deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Contract not found")
    except Exception as e:
        logger.error(f"Contract deletion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Существующие эндпоинты
@app.post("/check-purchase", response_model=RuleCheckResponse)
async def check_purchase(purchase_info: PurchaseInfo):
    """
    Проверяет покупку по бизнес-правилам
    """
    try:
        return rules_engine.check_purchase(purchase_info)
    except Exception as e:
        logger.error(f"Purchase check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process-purchase", response_model=TransactionResponse)
async def process_purchase(purchase_info: PurchaseInfo):
    """
    Обрабатывает покупку: проверяет правила и выполняет транзакцию через банк
    """
    try:
        # 1. Проверяем по бизнес-правилам
        rules_result = rules_engine.check_purchase(purchase_info)
        
        if not rules_result.allowed:
            raise HTTPException(
                status_code=400, 
                detail=f"Transaction not allowed: {rules_result.reason}. Details: {rules_result.details}"
            )
        
        # 2. Проверяем баланс через банковское API
        balance = bank_client.get_balance(purchase_info.card_number)
        if balance.balance < purchase_info.cost:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient funds. Balance: {balance.balance}, Required: {purchase_info.cost}"
            )
        
        # 3. Создаем запрос на перевод (платеж мерчанту)
        transfer_request = TransferRequest(
            from_card=purchase_info.card_number,
            to_card=f"MERCHANT_{purchase_info.merchant_id}",
            amount=purchase_info.cost
        )
        
        # 4. Выполняем транзакцию через банковское API
        transaction_result = bank_client.transfer(transfer_request)
        
        logger.info(f"Purchase processed successfully: {transaction_result.transaction_id}")
        return transaction_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Purchase processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process-purchase-with-contract")
async def process_purchase_with_contract(
    purchase_info: PurchaseInfo,
    contract_id: str
):
    """
    Обрабатывает покупку с дополнительной проверкой через смарт-контракт
    """
    try:
        # 1. Проверяем базовые правила (только сумма)
        rules_result = rules_engine.check_purchase(purchase_info)
        if not rules_result.allowed:
            raise HTTPException(
                status_code=400, 
                detail=f"Basic validation failed: {rules_result.reason}"
            )
        
        # 2. Проверяем через смарт-контракт
        contract_result = await contract_manager.execute_contract(contract_id, purchase_info)
        if not contract_result.allowed:
            raise HTTPException(
                status_code=400,
                detail=f"Contract violation: {contract_result.reason}"
            )
        
        # 3. Проверяем баланс
        balance = bank_client.get_balance(purchase_info.card_number)
        if balance.balance < purchase_info.cost:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient funds. Balance: {balance.balance}, Required: {purchase_info.cost}"
            )
        
        # 4. Выполняем транзакцию
        transfer_request = TransferRequest(
            from_card=purchase_info.card_number,
            to_card=f"MERCHANT_{purchase_info.merchant_id}",
            amount=purchase_info.cost
        )
        
        transaction_result = bank_client.transfer(transfer_request)
        logger.info(f"Purchase with contract processed: {transaction_result.transaction_id}")
        return transaction_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Purchase processing with contract failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cards/{card_number}/contracts")
async def get_card_contracts(card_number: str):
    """
    Получить все контракты, которые применяются к карте
    """
    try:
        contracts = contract_manager.get_contracts_for_card(card_number)
        return {
            "card_number": card_number,
            "applicable_contracts_count": len(contracts),
            "contracts": contracts
        }
    except Exception as e:
        logger.error(f"Error getting card contracts: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 

# Остальные эндпоинты
@app.post("/deposit", response_model=TransactionResponse)
async def deposit(request: DepositRequest):
    try:
        return bank_client.deposit(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/transfer", response_model=TransactionResponse)
async def transfer(request: TransferRequest):
    try:
        return bank_client.transfer(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/balance/{card_number}", response_model=BalanceResponse)
async def get_balance(card_number: str):
    try:
        return bank_client.get_balance(card_number)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/transactions/{card_number}", response_model=List[TransactionResponse])
async def get_transactions(card_number: str):
    try:
        return bank_client.get_transactions(card_number)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/rules/mcc")
async def get_mcc_rules():
    """
    Получить список MCC кодов и их лимитов
    """
    return rules_engine.mcc_limits

@app.get("/health")
async def health_check():
    try:
        bank_client.get_balance("test")
        return {"status": "healthy", "service": "smart-contract-bank-service"}
    except Exception as e:
        return {"status": "degraded", "bank_api": "unavailable", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)