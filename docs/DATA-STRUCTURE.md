# Data Structure Overview

## Core Entities
- **User** (auth): `id (UUID)`, `name`, `email (unique)`, `hashed_password`, `bank_id`.
- **GrantProgram** (grants): `id (UUID)`, `name`, `bank_account_number` (identifier used by payments/contracts), `stages[]`.
- **Stage** (grants): `id (UUID)`, `grant_program_id`, `order` (sequential), `amount` (Decimal), `completion_status` (`pending|active|completed`), `requirements[]`.
- **Requirement** (grants): `id (UUID)`, `stage_id`, `name`, `description`, `status` (`pending|completed`), `proof_url` (submitted evidence), `proof_submitted_by (UUID)`.
- **UserToGrant** (grants): `id (UUID)`, `user_id`, `grant_program_id`, `role` (`Grantor|Supervisor|Grantee`), `active`; API exposes linked user `email` and `name` for display.

## Relationships
- `GrantProgram 1<-*> Stage`: ordered stages per program.
- `Stage 1<-*> Requirement`: requirements attached to a stage.
- `User 1<-*> UserToGrant *>-1 GrantProgram`: role mapping between users and programs.

## Flows / Integrity
- Stage orders must be sequential starting at 1 (validated on creation).
- Stage completion requires all linked requirements to be `completed`; then a payout is triggered.
- Payments reference `grant_program.grant_receiver` as the participant identifier for MIR.

## Configuration
- Settings via `core.config.Settings` (Pydantic BaseSettings): `DB_URL`, `SECRET_KEY`, `MIR_API_KEY`, `MIR_API_BASE_URL`, etc.
- Database: async SQLAlchemy models inherit from `core.database.Base` (Postgres via asyncpg).

## Extensibility Notes
- Requirements status updates are not yet exposed; add CRUD/patch endpoints to manage requirement statuses.
- Contracts module is a stub; future contract metadata can attach to `GrantProgram` or `Stage` as needed.
