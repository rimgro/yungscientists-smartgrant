from sqlalchemy import create_engine, Column, String, Float, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import os
from models import TransactionType

# Получение URL базы данных из переменных окружения
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/bank_service.db")

# Для SQLite нужно указать check_same_thread=False
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class AccountDB(Base):
    __tablename__ = "accounts"
    
    card_number = Column(String, primary_key=True, index=True)
    balance = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class TransactionDB(Base):
    __tablename__ = "transactions"
    
    id = Column(String, primary_key=True, index=True)
    type = Column(Enum(TransactionType))
    amount = Column(Float)
    from_card = Column(String, nullable=True)
    to_card = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String, default="completed")
    description = Column(String, nullable=True)

# Создаем таблицы
def init_db():
    Base.metadata.create_all(bind=engine)
    
    # Инициализация тестовых данных
    db = SessionLocal()
    try:
        # Счет банка 131
        bank_account = db.query(AccountDB).filter(AccountDB.card_number == "131").first()
        if not bank_account:
            bank_account = AccountDB(card_number="131", balance=1000000.0)
            db.add(bank_account)
        
        # Тестовый счет пользователя
        user_account = db.query(AccountDB).filter(AccountDB.card_number == "4111111111111111").first()
        if not user_account:
            user_account = AccountDB(card_number="4111111111111111", balance=5000.0)
            db.add(user_account)
        
        db.commit()
        print("✅ База данных инициализирована")
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка инициализации базы данных: {e}")
    finally:
        db.close()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Инициализируем базу при импорте
init_db()