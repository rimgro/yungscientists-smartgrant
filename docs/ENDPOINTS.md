# SmartGrant API Endpoints (v1)

Base URL: `/api/v1`

## Auth
- `POST /auth/register` — Register a new user. Body: `{name, email, password, bank_id?}`. Returns user.
- `POST /auth/token` — Login with `{email, password}`. Returns bearer token.
- `GET /auth/me` — Current user profile. Requires `Authorization: Bearer <token>`.

## Grants
- `POST /grants` — Create a grant program with stages and requirements. Body includes stages `[ { order, amount, requirements[] } ]`.
- `GET /grants` — List grant programs with stages/requirements.
- `POST /grants/stages/{stage_id}/complete` — Mark a stage complete (requires all requirements completed). Triggers payout via payments service.

## Payments
- `POST /payments` — Send a targeted payment. Body: `{participant_id, amount, reference}`.
- `GET /payments/{transaction_id}` — Poll transaction status.

## Contracts
- `POST /contracts/{grant_program_id}/execute` — Placeholder to trigger contract interaction; currently returns stub.

## Health
- `GET /health` — Service liveness probe.
