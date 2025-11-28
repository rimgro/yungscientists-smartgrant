from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.core.security import get_current_user
from .schemas import Token, UserCreate, UserLogin, UserRead
from .services import AuthService, UserService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(payload: UserCreate, session: AsyncSession = Depends(get_session)) -> UserRead:
    service = UserService(session)
    return await service.register_user(payload)


@router.post("/token", response_model=Token)
async def login(credentials: UserLogin, session: AsyncSession = Depends(get_session)) -> Token:
    service = AuthService(session)
    return await service.login(credentials)


@router.get("/me", response_model=UserRead)
async def read_current_user(current_user=Depends(get_current_user)) -> UserRead:
    return UserRead.model_validate(current_user)
