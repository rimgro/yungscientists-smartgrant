# SmartGrant

SmartGrant is a grants management platform that coordinates grantees, supervisors, and grantors through staged milestones, payment controls, and smart-contract style rules. The stack is FastAPI + PostgreSQL for the API, SvelteKit for the client, and a stubbed MIR/fake-bank integration for payment flows.

## Stack
- FastAPI, SQLAlchemy (async), Alembic, JWT auth
- PostgreSQL (or SQLite for tests), fake bank + payment middleware adapters
- SvelteKit (CSR, TypeScript, Tailwind), Vite
- Docker/Docker Compose for full environment

## Repository Layout
- `backend/` – FastAPI app, Alembic migrations, tests
- `frontend/` – SvelteKit SPA, Tailwind UI
- `fake_bank/` – lightweight MIR-like sandbox service
- `docker-compose.yml` – full stack (frontend, API, Postgres, fake bank); dev/test profiles included
- `ARCHITECTURE.md`, `BACKEND-ARCHITECTURE.md`, `FRONTEND-ARCHITECTURE.md` – design notes

## Quickstart (Docker)
1. Ensure Docker and Docker Compose are installed.
2. Copy `backend/.env` and set secrets (e.g., `SECRET_KEY`, `MIR_API_KEY`); defaults work for local dev.
3. Build and start everything:
   ```sh
   docker compose up --build
   ```
   - Frontend: http://localhost:4173  
   - API & docs: http://localhost:8000 (Swagger at `/docs`)  
   - Fake bank sandbox: http://localhost:8010  
   - Postgres: `localhost:5432` (`smartgrant`/`smartgrant`)
4. To develop with live-reload for the frontend, use the dev profile:
   ```sh
   docker compose --profile dev up --build
   ```

## Local Development (without Docker)
### Backend
```sh
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# configure environment: copy/update .env (DB_URL, SECRET_KEY, MIR_API_KEY, etc.)
alembic upgrade head  # migrate schema
uvicorn src.main:app --reload --port 8000
```
- Point `DB_URL` to a running Postgres instance (e.g., `postgresql+asyncpg://smartgrant:smartgrant@localhost:5432/smartgrant`).

### Frontend
```sh
cd frontend
npm install
PUBLIC_API_BASE_URL=http://localhost:8000 npm run dev -- --host --port 4173
```

## Tests
- API: `docker compose --profile test up --build api-tests` or `cd backend && pytest`
- Frontend: `cd frontend && npm test` (unit) or `npm run e2e` (Playwright, requires API running)

## Useful URLs
- Frontend app: http://localhost:4173
- API Swagger: http://localhost:8000/docs
- API health check: http://localhost:8000/api/v1/health
- Fake bank UI: http://localhost:8010

## Notes
- SPA mode is enabled (`ssr = false`); static builds are served via Nginx in Docker.
- Payment middleware endpoints are namespaced under `/api/v1/payment-middleware`.
