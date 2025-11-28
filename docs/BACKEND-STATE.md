# Backend State (current)

## Stack
- FastAPI app under `backend/src/main.py` with modular routers and async SQLAlchemy.
- Postgres via Docker Compose; config from `backend/.env`.
- Pydantic v2 schemas, JWT auth, httpx for external calls.

## Modules & Features
- **Auth**: User model (UUID id, name, email, hashed_password, bank_id). Register, login (JWT bearer), get current user. Password hashing with passlib/bcrypt; JWT with python-jose.
- **Grants**:
  - GrantProgram now stores `bank_account_number`, `status` (`draft|active|completed`), and `grantor_id`.
  - Participants tracked via `UserToGrant` with roles `grantor|grantee|supervisor` (unique per user/grant).
  - Creation: authenticated user becomes grantor automatically; optional participant invites inline.
  - Confirmation endpoint activates stage 1 (others pending) and moves grant to `active`; last stage completion sets grant `completed`.
  - Stage completion restricted to grantor/supervisor, requires active stage and completed requirements, triggers payout to the grant bank account.
  - Requirement completion restricted to grantor/supervisor and only on active stages.
  - Endpoints for invites, confirmation, requirement completion, and sequential stage flow.
- **Payments**: SimplePaymentGateway wraps MIR API (async httpx) for participant lookup, payments, and polling. Stage payout uses the grant's bank account number. Payment service routes: send payment, poll status. Env-driven API key/base URL.
- **Contracts**: Stub service/router to trigger future blockchain actions; currently returns a placeholder response.

## Infrastructure
- `docker-compose.yml` at repo root builds `backend/Dockerfile`, mounts `backend/src`, and runs API on `:8000` + Postgres on `:5432`.
- `.env.example` in `backend/` documents required settings; copied to `backend/.env` for local compose.
- Auto-creates tables on startup in `lifespan`; migrations not yet wired (Alembic dependency present but unused).
- CORS enabled for `http://localhost:4173` and `http://127.0.0.1:4173`.

## Gaps / Next Steps
- Alembic migrations instead of runtime `create_all`.
- Contracts module is a stub; business logic for requirements completion and stage payouts can be expanded (e.g., mark requirement status, proper receiver resolution for payouts).
- Pydantic models still use deprecated `Config` style; consider migrating to `ConfigDict`.
- Expand test coverage beyond current grant lifecycle happy path.
