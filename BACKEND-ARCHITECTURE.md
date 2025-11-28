# Architectural Requirements: SmartGrant System

## 1. High-Level Architecture
The system will follow a **Modular Monolith** architecture using **FastAPI**. The application must be structured into distinct domains (modules) to ensure separation of concerns, maintainability, and scalability.

### 1.1 Core Principles
- **Domain-Driven Design (DDD):** Modules are organized by business context (e.g., Grants, Payments, Users) rather than technical layers.
- **Dependency Injection:** Use FastAPI's `Depends` for injecting services and repositories.
- **Asynchronous I/O:** Fully leverage `async/await` for I/O-bound operations (Database, External APIs, Blockchain).

## 2. Project Structure
The codebase must adhere to the following directory structure:

~~~
src/
├── core/                   # Global configs, exceptions, security
│   ├── config.py           # Pydantic BaseSettings
│   ├── security.py         # JWT handling, hashing
│   └── database.py         # Async engine, session factory
├── modules/                # Domain-specific modules
│   ├── auth/               # User management & authentication
│   ├── grants/             # Grant programs, stages, requirements
│   ├── payments/           # Mir payment system integration
│   └── contracts/          # Smart contract interaction layer
├── main.py                 # App entrypoint, router aggregation
└── requirements.txt
~~~

## 3. Module Specifications

### 3.1 Auth Module (`src/modules/auth`)
**Responsibility:** User registration, login, and role management.
- **Entities:** `User` (id, name, email, hashed_password, bank_id).
- **Services:**
  - `AuthService`: Handle login logic and JWT token generation.
  - `UserService`: CRUD for users.
- **Security:** Implement OAuth2 with Password Flow (Bearer Token).

### 3.2 Grants Module (`src/modules/grants`)
**Responsibility:** Managing the lifecycle of grants, stages, and compliance requirements.
- **Entities:**
  - `GrantProgram` (stages, grant_receiver).
  - `Stage` (order, amount, requirements, completion_status).
  - `Requirement` (name, description, status).
  - `UserToGrant` (mapping users to grants with roles: Grantor, Supervisor, Grantee).
- **Logic:**
  - Ensure stages are ordered sequentially.
  - Validate that stage completion triggers updates to send the money using an API (payments module).

### 3.3 Payments Module (`src/modules/payments`)
**Responsibility:** Integration with the Mir Payment System API.
- **Core Functionality:**
  - **Adapter Pattern:** Create a `SimplePaymentGateway` class to wrap external API calls.
  - **Features:** Participant identification, targeted transfers, transaction status polling.
- **Requirements:**
  - All external API calls must be asynchronous (`httpx` is recommended).
  - Sensitive data (API keys, certificates) must be loaded from environment variables.

## 4. Technical Standards

### 4.1 Database & ORM
- **Library:** SQLAlchemy (Async) + Alembic for migrations.
- **Schema:** Define tables matching `entities.md`. Use foreign keys for relationships (e.g., `Stage` -> `GrantProgram`).
- **Pattern:** Use the **Repository Pattern** to isolate database queries from business logic.

### 4.2 API Interface
- **Serialization:** Use **Pydantic v2** models for all request/response schemas.
- **Documentation:** maintain clear OpenAPI (Swagger) docs with descriptions for all endpoints.
- **Versioning:** Prefix all routes with `/api/v1`.
- **Modularity:** Different modules should have their own APIs.

### 4.3 Testing & Quality
- **Testing:** `pytest` with `AsyncClient` for integration tests.
- **Linting:** `ruff` or `flake8` for code style.

## 5. Deployment & Configuration
- **Environment:** All config (DB_URL, MIR_API_KEY, SECRET_KEY) must be managed via `.env` files.
- **Docker:** Provide a `Dockerfile` and `docker-compose.yml` for spinning up the API and the database.
