from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.database import Base, engine
from src.modules.auth import router as auth_router
from src.modules.grants import router as grants_router
from src.modules.payments import router as payments_router
from src.modules.contracts import router as contracts_router
from src.modules.payment_middleware import router as payment_middleware_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Dev fallback to create tables (production should use Alembic migrations).
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="SmartGrant API", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4173",
        "http://127.0.0.1:4173",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_PREFIX = "/api/v1"
app.include_router(auth_router.router, prefix=API_PREFIX)
app.include_router(grants_router.router, prefix=API_PREFIX)
app.include_router(payments_router.router, prefix=API_PREFIX)
app.include_router(contracts_router.router, prefix=API_PREFIX)
app.include_router(payment_middleware_router.router, prefix=API_PREFIX)


@app.get(f"{API_PREFIX}/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
