from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid
import datetime
from typing import List

from database import get_db, AccountDB, TransactionDB
from models import (
    DepositRequest, 
    TransferRequest, 
    TransactionResponse, 
    AccountBalance,
    TransactionType
)

app = FastAPI(
    title="Bank Service API",
    description="API для банковских операций с банком 131",
    version="1.0.0"
)


def get_account(db: Session, card_number: str) -> AccountDB:
    account = db.query(AccountDB).filter(AccountDB.card_number == card_number).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Счет с номером карты {card_number} не найден"
        )
    return account

@app.post("/deposit", response_model=TransactionResponse)
async def deposit_money(
    request: DepositRequest,
    db: Session = Depends(get_db)
):

    if not (request.card_number):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный формат номера карты"
        )
    
    # Получаем или создаем счет
    account = db.query(AccountDB).filter(AccountDB.card_number == request.card_number).first()
    if not account:
        account = AccountDB(card_number=request.card_number, balance=0.0)
        db.add(account)
    
    # Пополняем счет
    account.balance += request.amount
    
    # Создаем запись о транзакции
    transaction = TransactionDB(
        id=str(uuid.uuid4()),
        type=TransactionType.DEPOSIT,
        amount=request.amount,
        to_card=request.card_number,
        status="completed",
        description=f"Пополнение счета на {request.amount} RUB"
    )
    
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    
    return TransactionResponse(
        transaction_id=transaction.id,
        type=transaction.type,
        amount=request.amount,
        card_number=request.card_number,
        timestamp=transaction.timestamp,
        status=transaction.status,
        message=f"Счет успешно пополнен на {request.amount} RUB"
    )

@app.post("/transfer", response_model=TransactionResponse)
async def transfer_money(
    request: TransferRequest,
    db: Session = Depends(get_db)
):
    # Валидация карт
    if not (request.from_card) or not (request.to_card):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный формат номера карты"
        )
    
    if request.from_card == request.to_card:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя переводить деньги на ту же карту"
        )
    
    # Получаем счет отправителя
    from_account = get_account(db, request.from_card)
    
    # Проверяем достаточность средств
    if from_account.balance < request.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Недостаточно средств на счете"
        )
    
    # Получаем или создаем счет получателя
    to_account = db.query(AccountDB).filter(AccountDB.card_number == request.to_card).first()
    if not to_account:
        to_account = AccountDB(card_number=request.to_card, balance=0.0)
        db.add(to_account)
    
    # Выполняем перевод
    from_account.balance -= request.amount
    to_account.balance += request.amount
    
    # Создаем запись о транзакции
    transaction = TransactionDB(
        id=str(uuid.uuid4()),
        type=TransactionType.TRANSFER,
        amount=request.amount,
        from_card=request.from_card,
        to_card=request.to_card,
        status="completed",
        description=request.description or f"Перевод на карту {request.to_card}"
    )
    
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    
    return TransactionResponse(
        transaction_id=transaction.id,
        type=transaction.type,
        amount=request.amount,
        card_number=request.to_card,
        timestamp=transaction.timestamp,
        status=transaction.status,
        message=f"Успешный перевод {request.amount} RUB на карту {request.to_card}"
    )

@app.get("/balance/{card_number}", response_model=AccountBalance)
async def get_balance(
    card_number: str,
    db: Session = Depends(get_db)
):

    if not (card_number):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный формат номера карты"
        )
    
    account = get_account(db, card_number)
    
    return AccountBalance(
        card_number=account.card_number,
        balance=account.balance
    )

@app.get("/transactions/{card_number}", response_model=List[TransactionResponse])
async def get_transactions(
    card_number: str,
    db: Session = Depends(get_db)
):
    """
    Получение истории транзакций по карте
    """
    if not (card_number):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный формат номера карты"
        )
    
    transactions = db.query(TransactionDB).filter(
        (TransactionDB.from_card == card_number) | (TransactionDB.to_card == card_number)
    ).order_by(TransactionDB.timestamp.desc()).limit(50).all()
    
    response_transactions = []
    for transaction in transactions:
        if transaction.type == TransactionType.DEPOSIT:
            card_num = transaction.to_card
        else:
            card_num = transaction.to_card if transaction.to_card != card_number else transaction.from_card
        
        response_transactions.append(TransactionResponse(
            transaction_id=transaction.id,
            type=transaction.type,
            amount=transaction.amount,
            card_number=card_num,
            timestamp=transaction.timestamp,
            status=transaction.status,
            message=transaction.description or ""
        ))
    
    return response_transactions

@app.get("/")
async def root():
    return {
        "message": "Bank Service API",
        "version": "1.0.0",
        "endpoints": {
            "deposit": "POST /deposit - Пополнение счета",
            "transfer": "POST /transfer - Перевод денег",
            "balance": "GET /balance/{card_number} - Получение баланса",
            "transactions": "GET /transactions/{card_number} - История транзакций"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)