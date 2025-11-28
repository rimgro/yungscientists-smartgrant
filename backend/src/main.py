from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.core.database import Base, engine
from src.modules.auth import router as auth_router
from src.modules.grants import router as grants_router
from src.modules.payments import router as payments_router
from src.modules.contracts import router as contracts_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-create tables for local/dev; replace with Alembic migrations in production.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="SmartGrant API", version="1.0.0", lifespan=lifespan)

API_PREFIX = "/api/v1"
app.include_router(auth_router.router, prefix=API_PREFIX)
app.include_router(grants_router.router, prefix=API_PREFIX)
app.include_router(payments_router.router, prefix=API_PREFIX)
app.include_router(contracts_router.router, prefix=API_PREFIX)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
