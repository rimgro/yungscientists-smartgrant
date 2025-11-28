# Frontend ⇄ Backend Alignment Guide

Short checklist to keep UI and API in sync and avoid unplanned surface area.

## Data model alignment
- Canonical receiver field is `bank_account_number` (backend + payouts). Use that label in UI and payloads; if you prefer `grant_receiver`, rename the backend field and adjust docs/UI together.
- Backend stage schema: `order`, `amount`, `completion_status`, `requirements[{name, description, status}]`. Remove unused UI fields (`stage.name`, `stage.due`, `Stage.grant_program_id`, `Requirement.stage_id`) or add them to backend models/schemas if truly needed.
- Grant statuses: `draft|active|completed`. Stage statuses: `pending|active|completed`. Render accordingly; fallback title is `Stage {order}` if no name exists.

## Flow fixes
- After creating a grant, immediately POST `/grants/{id}/confirm` so stage 1 becomes `active`; otherwise requirement/stage actions 400.
- Grant creation wizard should build payload with `stages: [{order, amount, requirements: [...] }]` and optional participants. Drop fields the API ignores.

## Permissions UX
- Only grantor/supervisor may complete requirements or stages. Hide/disable those actions for other roles and show a message on 403 instead of exposing broken buttons.

## Trim or label stubs
- Payment/contract widgets (wallet connect, transaction history, contract status) are static; hide them or label as “stub” until wired to real endpoints.
- Requirement upload component has no API; hide or mark planned.

## Docs sync
- Keep `docs/DATA-STRUCTURE.md` consistent with the chosen receiver field and any added/removed stage or requirement attributes.
