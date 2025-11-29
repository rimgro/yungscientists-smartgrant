# Architectural Requirements: SmartGrant Frontend (SPA)

## 1. High-Level Architecture
The frontend will be built as a **Single Page Application (SPA)** using **SvelteKit**. All rendering will occur on the client side (CSR), allowing the application to be served as a static asset bundle. This ensures full decoupling from the backend and enables easy deployment to static hosting (e.g., Nginx, S3).

### 1.1 Core Principles
- **Client-Side Rendering (CSR):** The application will load once and handle routing dynamically in the browser. Server-Side Rendering (SSR) must be disabled.
- **Component-Based Architecture:** UI elements must be reusable and atomic (e.g., Button, Card) vs. feature-specific.
- **Type Safety:** Strict use of **TypeScript** throughout components and logic.
- **Reactive State:** Use Svelte Stores for global state management (User Session, Notifications) and client-side API calls for data fetching.

## 2. Project Structure
The codebase must adhere to the following directory structure, utilizing SvelteKit's route grouping features:

~~~
src/
├── lib/
│   ├── components/         # Shared generic UI (Buttons, Modals, Inputs)
│   ├── features/           # Business logic grouped by domain
│   │   ├── auth/           # Login forms, validation schemas
│   │   ├── grants/         # Grant cards, stage viz, wizards
│   │   └── payments/       # Transaction tables, wallet widgets
│   ├── stores/             # Global Svelte stores (auth, toasts)
│   └── api.ts              # Axios/Fetch wrapper with interceptors
├── routes/
│   ├── +layout.ts          # Global CSR settings (ssr = false)
│   ├── (auth)/             # Public auth pages (login, register)
│   ├── (app)/              # Protected application routes
│   │   ├── grants/
│   │   │   ├── [id]/       # Grant details & management
│   │   │   └── new/        # Grant creation wizard
│   │   └── profile/        # User settings & bank integration
│   └── +layout.svelte      # Root layout (Nav, Footer, Auth Check)
├── app.html
└── static/                 # Static assets (logos, global css)
~~~

## 3. Module Specifications

### 3.1 Auth Module (`lib/features/auth`)
**Responsibility:** Authentication UI and client-side session persistence.
- **Components:** `LoginForm`, `RegisterForm`.
- **Logic:**
  - Store JWT in `localStorage` or `sessionStorage` (since no backend session cookies).
  - **Protected Routes:** Logic in a generic `AuthGuard` component or `+layout.svelte` to check for the token and redirect unauthenticated users to `/login`.

### 3.2 Grants Module (`lib/features/grants`)
**Responsibility:** Visualization and management of the grant lifecycle.
- **Components:**
  - `GrantCreationWizard`: Multi-step form to define Stages and Requirements.
  - `StageTracker`: Visual progress bar showing the current state of the grant.
  - `RequirementUpload`: File dropzone or form for Grantees to submit proof of work.
- **Role Logic:**
  - **Grantee:** Sees "Upload/Submit" actions.
  - **Supervisor/Grantor:** Sees "Approve/Reject" actions and "Edit Limits" controls.

### 3.3 Payments & Contracts UI (`lib/features/payments`)
**Responsibility:** Financial transparency and Smart Contract status components embedded within grant pages.
- **Components:**
  - `WalletConnect`: UI to link/display Mir payment system status.
  - `TransactionHistory`: Table displaying ledger events (funds locked, transferred).
  - `ContractStatus`: Visual indicator (Chip/Badge) showing the smart contract state (e.g., "Awaiting Oracle", "Disbursed").

## 4. Technical Standards

### 4.1 Styling & UI Framework
- **Framework:** **Tailwind CSS** for utility-first styling.
- **Component Library:** Use a lightweight headless library (e.g., Skeleton UI or shadcn-svelte) for accessible primitives.
- **Design System:** Define a `theme.css` for primary colors (matching Mir/Corporate branding) to ensure consistency.

### 4.2 Data Fetching & State
- **CSR Configuration:** Set `export const ssr = false;` in the root `src/routes/+layout.ts` to force SPA mode.
- **Pattern:** Use `onMount` or SvelteKit `load` functions (running on client only) to fetch data.
- **API Client:** Create a wrapper around `fetch` in `src/lib/api.ts` that:
  - Automatically attaches the `Authorization: Bearer` token from local storage.
  - Handles 401 errors by redirecting to `/login`.
- **Form Handling:** Use **Superforms** (client-side mode) or **Svelte-hook-form** for validation (Zod integration).

### 4.3 Testing & Quality
- **Unit Testing:** `Vitest` for testing independent components and utility functions.
- **E2E Testing:** `Playwright` for critical flows (Login -> Create Grant -> Approve).
- **Linting:** `ESLint` + `Prettier` with the Svelte plugin.

## 5. Deployment & Configuration
- **Adapter:** Use `@sveltejs/adapter-static` with `fallback: 'index.html'` configuration. This is critical for SPA routing support on static hosts.
- **Environment:** Public variables (API Base URL) prefixed with `PUBLIC_` in `.env`.
- **Docker:** Dockerfile should use a Node builder stage to compile static assets, then copy them to an **Nginx** container for serving.
