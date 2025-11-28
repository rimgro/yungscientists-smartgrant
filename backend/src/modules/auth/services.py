from datetime import timedelta

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core import security
from src.core.config import settings
from .models import User
from .repositories import UserRepository
from .schemas import Token, UserCreate, UserLogin, UserRead


class UserService:
    def __init__(self, session: AsyncSession):
        self.repo = UserRepository(session)
        self.session = session

    async def register_user(self, payload: UserCreate) -> UserRead:
        existing = await self.repo.get_by_email(payload.email)
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

        hashed_password = security.get_password_hash(payload.password)
        user = User(
            name=payload.name,
            email=payload.email,
            hashed_password=hashed_password,
            bank_id=payload.bank_id,
        )
        await self.repo.create(user)
        await self.session.commit()
        await self.session.refresh(user)
        return UserRead.model_validate(user)

    async def list_users(self) -> list[UserRead]:
        users = await self.repo.list()
        return [UserRead.model_validate(u) for u in users]


class AuthService:
    def __init__(self, session: AsyncSession):
        self.repo = UserRepository(session)
        self.session = session

    async def login(self, credentials: UserLogin) -> Token:
        user = await self.repo.get_by_email(credentials.email)
        if not user or not security.verify_password(credentials.password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        access_token = security.create_access_token(
            data={"sub": str(user.id)}, expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
        )
        return Token(access_token=access_token)
