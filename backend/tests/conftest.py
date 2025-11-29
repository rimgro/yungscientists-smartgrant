import os
import sys
from pathlib import Path
from typing import Callable

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Force test env so settings loads against local sqlite, not docker .env.
os.environ["DB_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["SECRET_KEY"] = "test-secret"
os.environ["MIR_API_KEY"] = "test-key"
os.environ["APP_BANK_ACCOUNT_NUMBER"] = "APP-ACCOUNT"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.main import app  # noqa: E402
from src.core.database import Base, get_session  # noqa: E402
from src.core.security import get_current_user  # noqa: E402
from src.modules.auth.models import User  # noqa: E402
from src.modules.payments.services import PaymentService  # noqa: E402


@pytest_asyncio.fixture
async def session_factory():
    engine = create_async_engine(os.environ["DB_URL"], future=True)
    SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    try:
        yield SessionLocal
    finally:
        await engine.dispose()


@pytest_asyncio.fixture
async def client(session_factory):
    async def override_get_session():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as async_client:
        yield async_client

    app.dependency_overrides.pop(get_session, None)
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture(autouse=True)
def patch_payments(monkeypatch):
    async def _noop(self, stage):
        return None

    monkeypatch.setattr(PaymentService, "send_stage_payout", _noop)


async def create_user(session_factory, name: str, email: str) -> User:
    async with session_factory() as session:
        user = User(name=name, email=email, hashed_password="pwd")
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


@pytest_asyncio.fixture
async def users(session_factory):
    grantor = await create_user(session_factory, "Grantor", "grantor@example.com")
    grantee = await create_user(session_factory, "Grantee", "grantee@example.com")
    supervisor = await create_user(session_factory, "Supervisor", "supervisor@example.com")
    extra_supervisor = await create_user(session_factory, "Extra Supervisor", "extra.supervisor@example.com")
    return {
        "grantor": grantor,
        "grantee": grantee,
        "supervisor": supervisor,
        "extra_supervisor": extra_supervisor,
    }


@pytest.fixture
def use_current_user() -> Callable[[User], None]:
    def _set(user: User) -> None:
        async def _override():
            return user

        app.dependency_overrides[get_current_user] = _override

    return _set
