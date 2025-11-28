import logging
from typing import Dict, Any, List
from models import PurchaseInfo, RuleCheckResponse

class RulesEngine:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def check_purchase(self, purchase_info: PurchaseInfo) -> RuleCheckResponse:
        """
        Упрощенная проверка - только базовые валидации
        Без MCC ограничений, если нет контрактов
        """
        rules_checked = []
        details = {}
        
        # Только базовые проверки
        amount_rule_passed = self._check_amount_rule(purchase_info, details)
        rules_checked.append("Amount validation")
        
        # MCC и Merchant проверки убраны - они будут в контрактах
        
        allowed = amount_rule_passed
        
        reason = None if allowed else "Basic validation failed"
        
        return RuleCheckResponse(
            allowed=allowed,
            reason=reason,
            rules_checked=rules_checked,
            details=details
        )
    
    def _check_amount_rule(self, purchase: PurchaseInfo, details: Dict[str, Any]) -> bool:
        """Проверяет только базовые правила по сумме"""
        if purchase.cost <= 0:
            details["amount_check"] = "Amount must be positive"
            return False
        
        if purchase.cost > 1000000:  # Очень высокий лимит на случай ошибок
            details["amount_check"] = f"Amount {purchase.cost} exceeds maximum limit"
            return False
        
        details["amount_check"] = f"Amount {purchase.cost} is valid"
        return True