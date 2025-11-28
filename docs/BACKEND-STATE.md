# Backend State (current)

## Stack
- FastAPI app under `backend/src/main.py` with modular routers and async SQLAlchemy.
- Postgres via Docker Compose; config from `backend/.env`.
- Pydantic v2 schemas, JWT auth, httpx for external calls.

## Modules & Features
- **Auth**: User model (UUID id, name, email, hashed_password, bank_id). Register, login (JWT bearer), get current user. Password hashing with passlib/bcrypt; JWT with python-jose.
- **Grants**: GrantProgram, Stage (ordered, amount, completion_status), Requirement, UserToGrant. Create programs with sequential stage validation, list programs, complete stage (requires all requirements completed) then triggers payment.
- **Payments**: SimplePaymentGateway wraps MIR API (async httpx) for participant lookup, payments, and polling. Payment service routes: send payment, poll status. Env-driven API key/base URL.
- **Contracts**: Stub service/router to trigger future blockchain actions; currently returns a placeholder response.

## Infrastructure
- `docker-compose.yml` at repo root builds `backend/Dockerfile`, mounts `backend/src`, and runs API on `:8000` + Postgres on `:5432`.
- `.env.example` in `backend/` documents required settings; copied to `backend/.env` for local compose.
- Auto-creates tables on startup in `lifespan`; migrations not yet wired (Alembic dependency present but unused).

## Gaps / Next Steps
- Alembic migrations instead of runtime `create_all`.
- Tests (pytest/async) not written yet.
- Contracts module is a stub; business logic for requirements completion and stage payouts can be expanded (e.g., mark requirement status, proper receiver resolution for payouts).
