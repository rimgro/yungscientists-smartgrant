```markdown
# Bank Smart Contracts API Documentation

## Overview

REST API для управления банковскими операциями с системой смарт-контрактов. Позволяет создавать гибкие правила для ограничения транзакций по MCC кодам, мерчантам, суммам и времени.

**Base URL:** `http://localhost:8001`

## Quick Start

### 1. Проверка здоровья сервиса
```bash
curl http://localhost:8001/health
```

### 2. Создание первого смарт-контракта
```bash
curl -X POST http://localhost:8001/contracts \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My First Contract",
    "contract_type": "mcc_limit", 
    "parameters": {
      "allowed_mcc": ["5411", "5812"],
      "blocked_mcc": ["4121"],
      "applicable_cards": ["4111111111111111"]
    }
  }'
```

### 3. Выполнение покупки с контрактом
```bash
curl -X POST "http://localhost:8001/process-purchase-with-contract?contract_id=CONTRACT_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "mcc": "5411",
    "cost": 1500.50,
    "merchant_id": "supermarket_001",
    "card_number": "4111111111111111"
  }'
```

## API Endpoints

### Health Check
**GET** `/health`

Проверка доступности сервиса и банковского API.

**Response:**
```json
{
  "status": "healthy",
  "service": "smart-contract-bank-service",
  "bank_api": "available"
}
```

### Smart Contracts Management

#### Create Contract
**POST** `/contracts`

Создает новый смарт-контракт.

**Body:**
```json
{
  "name": "Contract Name",
  "contract_type": "mcc_limit|merchant_block|amount_limit|time_restriction|card_restriction",
  "description": "Optional description",
  "parameters": {
    // Зависит от типа контракта
  }
}
```

#### List Contracts
**GET** `/contracts`

Возвращает список всех созданных контрактов.

**Response:**
```json
[
  {
    "contract_id": "uuid",
    "name": "Contract Name", 
    "contract_type": "mcc_limit",
    "parameters": {...},
    "description": "Description",
    "status": "active",
    "created_at": "2024-01-15T14:30:00.000Z"
  }
]
```

#### Execute Contract
**POST** `/contracts/execute`

Выполняет контракт для проверки покупки (без выполнения транзакции).

**Body:**
```json
{
  "contract_id": "uuid",
  "purchase_info": {
    "mcc": "5411",
    "cost": 1500.50,
    "merchant_id": "merchant_001",
    "card_number": "4111111111111111"
  }
}
```

#### Delete Contract
**DELETE** `/contracts/{contract_id}`

Удаляет смарт-контракт.

### Purchase Processing

#### Check Purchase
**POST** `/check-purchase`

Проверяет покупку по базовым правилам (без контрактов).

**Body:**
```json
{
  "mcc": "5411",
  "cost": 1500.50,
  "merchant_id": "merchant_001", 
  "card_number": "4111111111111111"
}
```

**Response:**
```json
{
  "allowed": true,
  "reason": null,
  "rules_checked": ["Amount validation"],
  "details": {
    "amount_check": "Amount 1500.5 is valid"
  }
}
```

#### Process Purchase
**POST** `/process-purchase`

Выполняет покупку с базовой проверкой.

**Body:** (аналогично check-purchase)

**Response:**
```json
{
  "transaction_id": "uuid",
  "status": "completed", 
  "amount": 1500.5,
  "type": "transfer",
  "timestamp": "2024-01-15T14:30:00.000Z"
}
```

#### Process Purchase with Contract
**POST** `/process-purchase-with-contract?contract_id={contract_id}`

Выполняет покупку с проверкой через смарт-контракт.

**Body:** (аналогично check-purchase)

### Bank Operations

#### Deposit
**POST** `/deposit`

Пополнение счета карты.

**Body:**
```json
{
  "card_number": "4111111111111111",
  "amount": 10000.00
}
```

#### Transfer
**POST** `/transfer`

Перевод между картами.

**Body:**
```json
{
  "from_card": "4111111111111111",
  "to_card": "4222222222222222", 
  "amount": 5000.00
}
```

#### Get Balance
**GET** `/balance/{card_number}`

Получение баланса карты.

**Response:**
```json
{
  "card_number": "4111111111111111",
  "balance": 15000.0,
  "currency": "RUB"
}
```

#### Get Transactions
**GET** `/transactions/{card_number}`

История транзакций по карте.

**Response:**
```json
[
  {
    "transaction_id": "uuid",
    "status": "completed",
    "amount": 1500.5,
    "type": "transfer",
    "timestamp": "2024-01-15T14:30:00.000Z"
  }
]
```

#### Get Card Contracts
**GET** `/cards/{card_number}/contracts`

Получить контракты, применяемые к карте.

**Response:**
```json
{
  "card_number": "4111111111111111",
  "applicable_contracts_count": 2,
  "contracts": [...]
}
```

## Contract Types

### 1. MCC Limit (`mcc_limit`)
Ограничения по Merchant Category Codes.

**Parameters:**
```json
{
  "allowed_mcc": ["5411", "5812"],
  "blocked_mcc": ["4121"],
  "applicable_cards": ["4111111111111111", "4222222222222222"]
}
```

**Logic:**
- Если `allowed_mcc` не пустой - разрешены только указанные MCC
- Если `allowed_mcc` пустой - разрешены все MCC кроме `blocked_mcc`
- `blocked_mcc` - всегда блокирует указанные MCC

### 2. Merchant Block (`merchant_block`)
Блокировка конкретных мерчантов.

**Parameters:**
```json
{
  "blocked_merchants": ["merchant_risk_001", "suspicious_store"],
  "applicable_cards": ["all"]
}
```

### 3. Amount Limit (`amount_limit`)
Ограничение максимальной суммы транзакции.

**Parameters:**
```json
{
  "max_amount": 5000,
  "applicable_cards": ["4111111111111111"]
}
```

### 4. Time Restriction (`time_restriction`)
Ограничение по времени суток.

**Parameters:**
```json
{
  "restricted_hours": [23, 0, 1, 2, 3, 4, 5],
  "applicable_cards": ["all"]
}
```

### 5. Card Restriction (`card_restriction`)
Ограничения по конкретным картам.

**Parameters:**
```json
{
  "allowed_cards": ["4111111111111111"],
  "blocked_cards": ["4222222222222222"],
  "applicable_cards": ["all"]
}
```

## Parameter: applicable_cards

Определяет, к каким картам применяется контракт:

- `["all"]` - применяется ко всем картам (по умолчанию)
- `["card1", "card2"]` - применяется только к указанным картам

Если карта не входит в `applicable_cards`, контракт пропускается (разрешает транзакцию).

## Business Logic

### Базовые правила (всегда применяются):
- Сумма должна быть положительной
- Максимальная сумма транзакции: 1,000,000 ₽ (защита от ошибок)
- Проверка достаточности баланса

### Смарт-контракты (опционально):
- Применяются только если карта в `applicable_cards`
- Если на карте нет контрактов - ограничений нет
- Можно комбинировать несколько контрактов

## Error Handling

### HTTP Status Codes:
- `200` - Успех
- `400` - Неверный запрос (валидация, нарушение контракта)
- `404` - Ресурс не найден (карта, контракт)
- `500` - Внутренняя ошибка сервиса

### Error Response Format:
```json
{
  "detail": "Error description"
}
```

## Common Use Cases

### 1. Ограничение корпоративных карт
```bash
# Запрет ночных транзакций для корпоративных карт
curl -X POST http://localhost:8001/contracts \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Corporate Night Limit",
    "contract_type": "time_restriction",
    "parameters": {
      "restricted_hours": [22, 23, 0, 1, 2, 3, 4, 5, 6],
      "applicable_cards": ["corp_card_001", "corp_card_002"]
    }
  }'
```

### 2. Блокировка рисковых мерчантов
```bash
# Блокировка мошеннических мерчантов
curl -X POST http://localhost:8001/contracts \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Block Fraud Merchants", 
    "contract_type": "merchant_block",
    "parameters": {
      "blocked_merchants": ["fraud_site_001", "suspicious_market"],
      "applicable_cards": ["all"]
    }
  }'
```

### 3. Лимиты для студенческих карт
```bash
# Ограничение суммы для студенческих карт
curl -X POST http://localhost:8001/contracts \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Student Card Limits",
    "contract_type": "amount_limit", 
    "parameters": {
      "max_amount": 3000,
      "applicable_cards": ["student_card_001", "student_card_002"]
    }
  }'
```

## Testing Data

### Демо-карты:
```bash
# Стандартные тестовые карты
"1234567812345678" - начальный баланс: 50,000 ₽
"8765432187654321" - начальный баланс: 100,000 ₽  
"1111222233334444" - начальный баланс: 15,000 ₽
```

### Пополнение баланса для тестирования:
```bash
curl -X POST http://localhost:8001/deposit \
  -H "Content-Type: application/json" \
  -d '{
    "card_number": "4111111111111111", 
    "amount": 50000
  }'
```

## Best Practices

1. **Сначала тестируйте контракты** через `/contracts/execute` перед реальными транзакциями
2. **Используйте понятные имена** для контрактов
3. **Регулярно проверяйте активные контракты** через `/contracts`
4. **Удаляйте неиспользуемые контракты** для очистки
5. **Всегда указывайте `applicable_cards`** для точечного применения правил

## Troubleshooting

### Контракт не применяется:
- Проверьте `applicable_cards` - содержит ли карту
- Убедитесь что статус контракта "active"
- Проверьте логику `allowed_mcc`/`blocked_mcc`

### Транзакция отклонена:
- Используйте `/check-purchase` для диагностики базовых правил
- Используйте `/contracts/execute` для проверки контракта
- Проверьте баланс карты через `/balance/{card_number}`

### Ошибки формата:
- Убедитесь в корректности JSON
- Проверьте типы данных параметров
- Убедитесь что все строки в двойных кавычках

