# SmartGrant API Endpoints (v1)

Base URL: `/api/v1`

## Auth
- `POST /auth/register` — Register a new user. Body: `{name, email, password, bank_id?}`. Returns user.
- `POST /auth/login` — Login with `{email, password}`. Returns bearer token.
- `GET /auth/me` — Current user profile. Requires `Authorization: Bearer <token>`.

## Grants
- `POST /grants` — Create a grant program. Authenticated user becomes grantor. Body: `{name, bank_account_number, stages:[{order, amount, requirements[] }], participants:[{user_id, role(grantee|supervisor)}]}`. Returns grant with participants (including grantor) and `status=draft`.
- `POST /grants/{grant_program_id}/confirm` — Grantor confirms a draft grant; sets grant `status=active`, activates stage 1, leaves later stages pending.
- `POST /grants/{grant_program_id}/invite` — Grantor invites a user as grantee or supervisor after creation. Body: `{user_id, role}`.
- `POST /grants/requirements/{requirement_id}/complete` — Grantor/supervisor marks a requirement complete. Stage must be active.
- `POST /grants/stages/{stage_id}/complete` — Grantor/supervisor completes the active stage when all requirements are done; triggers payout to the grant bank account and activates the next stage (or completes the grant when last stage closes).
- `GET /grants` — List grant programs with status, participants, stages, and requirements.

## Payments
- `POST /payments` — Send a targeted payment. Body: `{participant_id, amount, reference}`.
- `GET /payments/{transaction_id}` — Poll transaction status.

## Contracts
- `POST /contracts/{grant_program_id}/execute` — Placeholder to trigger contract interaction; currently returns stub.

## Health
- `GET /health` — Service liveness probe. (Base URL applies, so `/api/v1/health`.)
