import logging
import uuid
import os
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from models import PurchaseInfo, ContractCreateRequest, ContractResponse, ContractExecutionResponse

class ContractManager:
    def __init__(self, storage_path: str = "storage/contracts"):
        self.storage_path = storage_path
        self.logger = logging.getLogger(__name__)
        self.contracts: Dict[str, dict] = {}
        
        os.makedirs(storage_path, exist_ok=True)
        self._load_existing_contracts()

    def _load_existing_contracts(self):
        """Загружает существующие контракты"""
        try:
            for filename in os.listdir(self.storage_path):
                if filename.endswith('.json'):
                    contract_id = filename[:-5]
                    self._load_contract(contract_id)
        except Exception as e:
            self.logger.error(f"Error loading existing contracts: {e}")

    def _load_contract(self, contract_id: str) -> bool:
        """Загружает конкретный контракт"""
        try:
            contract_path = os.path.join(self.storage_path, f"{contract_id}.json")
            with open(contract_path, 'r', encoding='utf-8') as f:
                contract_data = json.load(f)
            self.contracts[contract_id] = contract_data
            return True
        except Exception as e:
            self.logger.error(f"Error loading contract {contract_id}: {e}")
            return False

    async def create_contract(self, request: ContractCreateRequest) -> ContractResponse:
        """Создает новый смарт-контракт"""
        contract_id = str(uuid.uuid4())
        
        try:
            self._validate_contract_parameters(request.contract_type, request.parameters)
            
            contract_data = {
                "contract_id": contract_id,
                "name": request.name,
                "contract_type": request.contract_type,
                "parameters": request.parameters,
                "description": request.description,
                "status": "active",
                "created_at": datetime.now().isoformat()
            }
            
            contract_path = os.path.join(self.storage_path, f"{contract_id}.json")
            with open(contract_path, 'w', encoding='utf-8') as f:
                json.dump(contract_data, f, ensure_ascii=False, indent=2)
            
            self.contracts[contract_id] = contract_data
            return ContractResponse(**contract_data)
                
        except Exception as e:
            self.logger.error(f"Error creating contract: {e}")
            contract_path = os.path.join(self.storage_path, f"{contract_id}.json")
            if os.path.exists(contract_path):
                os.remove(contract_path)
            raise

    def _validate_contract_parameters(self, contract_type: str, parameters: Dict[str, Any]):
        """Валидирует параметры контракта"""
        if "applicable_cards" not in parameters:
            parameters["applicable_cards"] = ["all"]
        elif not isinstance(parameters["applicable_cards"], list):
            raise ValueError("applicable_cards must be a list")
        
        if contract_type == "mcc_limit":
            if "allowed_mcc" not in parameters or not isinstance(parameters["allowed_mcc"], list):
                raise ValueError("MCC limit contract requires 'allowed_mcc' list")
            if "blocked_mcc" not in parameters:
                parameters["blocked_mcc"] = []
                
        elif contract_type == "merchant_block":
            if "blocked_merchants" not in parameters or not isinstance(parameters["blocked_merchants"], list):
                raise ValueError("Merchant block contract requires 'blocked_merchants' list")
                
        elif contract_type == "amount_limit":
            if "max_amount" not in parameters or not isinstance(parameters["max_amount"], (int, float)):
                raise ValueError("Amount limit contract requires 'max_amount' number")
                
        elif contract_type == "time_restriction":
            if "restricted_hours" not in parameters or not isinstance(parameters["restricted_hours"], list):
                raise ValueError("Time restriction contract requires 'restricted_hours' list")
            for hour in parameters["restricted_hours"]:
                if not isinstance(hour, int) or hour < 0 or hour > 23:
                    raise ValueError("Restricted hours must be integers between 0 and 23")
        
        elif contract_type == "card_restriction":
            if "allowed_cards" not in parameters or not isinstance(parameters["allowed_cards"], list):
                raise ValueError("Card restriction contract requires 'allowed_cards' list")
            if "blocked_cards" not in parameters:
                parameters["blocked_cards"] = []
        else:
            raise ValueError(f"Unknown contract type: {contract_type}")

    def get_contracts_for_card(self, card_number: str) -> List[dict]:
        """Возвращает все контракты, которые применяются к карте"""
        applicable_contracts = []
        
        for contract_id, contract in self.contracts.items():
            if contract.get('status') != 'active':
                continue
                
            applicable_cards = contract['parameters'].get('applicable_cards', ['all'])
            
            # Если контракт для всех карт или для конкретной карты
            if 'all' in applicable_cards or card_number in applicable_cards:
                applicable_contracts.append(contract)
        
        return applicable_contracts

    async def execute_contract(self, contract_id: str, purchase_info: PurchaseInfo) -> ContractExecutionResponse:
        """Выполняет смарт-контракт для проверки покупки"""
        if contract_id not in self.contracts:
            raise ValueError(f"Contract {contract_id} not found")
        
        contract = self.contracts[contract_id]
        
        try:
            # Проверяем применимость контракта к карте
            card_check_result = self._check_card_applicability(contract['parameters'], purchase_info.card_number)
            if not card_check_result['applicable']:
                return ContractExecutionResponse(
                    allowed=True,  # Контракт не применяется - пропускаем
                    reason=card_check_result.get('reason'),
                    contract_id=contract_id,
                    contract_name=contract['name'],
                    details={"card_applicability": card_check_result}
                )
            
            # Выполняем основную логику контракта
            result = self._execute_contract_logic(contract, purchase_info)
            return ContractExecutionResponse(
                allowed=result['allowed'],
                reason=result.get('reason'),
                contract_id=contract_id,
                contract_name=contract['name'],
                details=result.get('details')
            )
            
        except Exception as e:
            self.logger.error(f"Error executing contract {contract_id}: {e}")
            raise

    def _check_card_applicability(self, parameters: Dict[str, Any], card_number: str) -> Dict[str, Any]:
        """Проверяет, применяется ли контракт к данной карте"""
        applicable_cards = parameters.get('applicable_cards', ['all'])
        
        if 'all' in applicable_cards:
            return {"applicable": True, "reason": "Contract applies to all cards"}
        
        if card_number in applicable_cards:
            return {"applicable": True, "reason": f"Card {card_number} is in applicable cards list"}
        
        return {
            "applicable": False, 
            "reason": f"Card {card_number} not in applicable cards list",
            "details": {"applicable_cards": applicable_cards}
        }

    def _execute_contract_logic(self, contract: dict, purchase_info: PurchaseInfo) -> Dict[str, Any]:
        """Выполняет логику контракта"""
        contract_type = contract['contract_type']
        parameters = contract['parameters']
        
        if contract_type == "mcc_limit":
            return self._execute_mcc_limit(parameters, purchase_info)
        elif contract_type == "merchant_block":
            return self._execute_merchant_block(parameters, purchase_info)
        elif contract_type == "amount_limit":
            return self._execute_amount_limit(parameters, purchase_info)
        elif contract_type == "time_restriction":
            return self._execute_time_restriction(parameters, purchase_info)
        elif contract_type == "card_restriction":
            return self._execute_card_restriction(parameters, purchase_info)
        else:
            return {"allowed": False, "reason": f"Unknown contract type: {contract_type}"}

    def _execute_mcc_limit(self, parameters: Dict[str, Any], purchase_info: PurchaseInfo) -> Dict[str, Any]:
        """Логика ограничения по MCC кодам"""
        allowed_mcc = parameters.get('allowed_mcc', [])
        blocked_mcc = parameters.get('blocked_mcc', [])
        
        if allowed_mcc and purchase_info.mcc not in allowed_mcc:
            return {
                "allowed": False,
                "reason": f"MCC {purchase_info.mcc} not in allowed list",
                "details": {"allowed_mcc": allowed_mcc, "current_mcc": purchase_info.mcc}
            }
        
        if purchase_info.mcc in blocked_mcc:
            return {
                "allowed": False,
                "reason": f"MCC {purchase_info.mcc} is blocked",
                "details": {"blocked_mcc": blocked_mcc, "current_mcc": purchase_info.mcc}
            }
        
        return {"allowed": True, "reason": "MCC check passed"}

    def _execute_merchant_block(self, parameters: Dict[str, Any], purchase_info: PurchaseInfo) -> Dict[str, Any]:
        """Логика блокировки мерчантов"""
        blocked_merchants = parameters.get('blocked_merchants', [])
        
        if purchase_info.merchant_id in blocked_merchants:
            return {
                "allowed": False,
                "reason": f"Merchant {purchase_info.merchant_id} is blocked",
                "details": {"blocked_merchants": blocked_merchants, "current_merchant": purchase_info.merchant_id}
            }
        
        return {"allowed": True, "reason": "Merchant check passed"}

    def _execute_amount_limit(self, parameters: Dict[str, Any], purchase_info: PurchaseInfo) -> Dict[str, Any]:
        """Логика ограничения по сумме"""
        max_amount = parameters.get('max_amount', float('inf'))
        
        if purchase_info.cost > max_amount:
            return {
                "allowed": False,
                "reason": f"Amount {purchase_info.cost} exceeds limit {max_amount}",
                "details": {"max_amount": max_amount, "current_amount": purchase_info.cost}
            }
        
        return {"allowed": True, "reason": "Amount check passed"}

    def _execute_time_restriction(self, parameters: Dict[str, Any], purchase_info: PurchaseInfo) -> Dict[str, Any]:
        """Логика ограничения по времени"""
        restricted_hours = parameters.get('restricted_hours', [])
        current_hour = datetime.now().hour
        
        if current_hour in restricted_hours:
            return {
                "allowed": False,
                "reason": f"Transactions not allowed at hour {current_hour}:00",
                "details": {"restricted_hours": restricted_hours, "current_hour": current_hour}
            }
        
        return {"allowed": True, "reason": "Time check passed"}

    def _execute_card_restriction(self, parameters: Dict[str, Any], purchase_info: PurchaseInfo) -> Dict[str, Any]:
        """Логика ограничения по картам"""
        allowed_cards = parameters.get('allowed_cards', [])
        blocked_cards = parameters.get('blocked_cards', [])
        
        if allowed_cards and purchase_info.card_number not in allowed_cards:
            return {
                "allowed": False,
                "reason": f"Card {purchase_info.card_number} not in allowed list",
                "details": {"allowed_cards": allowed_cards, "current_card": purchase_info.card_number}
            }
        
        if purchase_info.card_number in blocked_cards:
            return {
                "allowed": False,
                "reason": f"Card {purchase_info.card_number} is blocked",
                "details": {"blocked_cards": blocked_cards, "current_card": purchase_info.card_number}
            }
        
        return {"allowed": True, "reason": "Card check passed"}

    async def list_contracts(self) -> List[ContractResponse]:
        """Возвращает список всех контрактов"""
        contracts = []
        for contract_id, contract_data in self.contracts.items():
            contracts.append(ContractResponse(**contract_data))
        return contracts

    async def delete_contract(self, contract_id: str) -> bool:
        """Удаляет контракт"""
        try:
            if contract_id in self.contracts:
                del self.contracts[contract_id]
            
            contract_path = os.path.join(self.storage_path, f"{contract_id}.json")
            if os.path.exists(contract_path):
                os.remove(contract_path)
            
            return True
        except Exception as e:
            self.logger.error(f"Error deleting contract {contract_id}: {e}")
            return False