# AGENTS.md — AI Software Engineering Team

Repository-level guidance for Cursor AI agents working across this monorepo.

---

## 1. Project Mission

**What:** A multi-agent AI platform that simulates a real software engineering team.

**Input:** A user prompt describing software to build.

**Output:** Generated, reviewable, deployable software artifacts.

**Current phase:** Phase 1 — Foundation Setup. Build foundation only; no feature creep.

**North star:** Production-style quality, not demo hacks.

---

## 2. Architecture Boundaries

### Monorepo layout

```
ai-software-engineering-team/
├── frontend/   → UI, client state, API consumption only
├── backend/    → FastAPI routes, LangGraph orchestration, LLM calls, business logic
├── docker/     → Sandbox execution environment definitions
├── docs/       → Architecture decisions, API contracts, runbooks
└── AGENTS.md   → This file
```

### Data flow

```
User → Next.js UI → FastAPI REST/SSE → LangGraph agents → LLM providers
                                      → Supabase (DB / Auth / Storage)
                                      → Docker sandbox
                                      → GitHub API
```

### Hard rules

- **Frontend** never calls Gemini, Groq, or Ollama directly.
- **Frontend** never uses Supabase service-role keys.
- **Backend** never renders React or serves static frontend assets (frontend and backend are separate deployables).
- **Agent orchestration** lives only in `backend/` (LangGraph).
- **Docker sandbox** is invoked only from the backend, never from the frontend.
- **GitHub API** calls are made only from the backend with server-side tokens.
- **Embeddings** (pgvector) are stored and queried from the backend only.

---

## 3. Frontend Coding Rules

### Approved stack

| Technology | Purpose |
|------------|---------|
| Next.js 16 | App Router, TypeScript |
| Tailwind CSS v4 | Styling |
| shadcn/ui | UI components (to be added) |
| Zustand | Client / UI state |
| TanStack Query | Server state and API communication |

Do not substitute libraries without explicit approval.

### Structure — Option B (no `src/`)

The frontend uses the **create-next-app layout without a `src/` directory**. Do not migrate to `src/app/`.

```
frontend/
├── app/           → routes, layouts, page-level Server Components
├── components/    → reusable UI (shadcn in components/ui/)
├── lib/           → utilities, API client, query client setup
├── hooks/         → custom React hooks
├── stores/        → Zustand stores
└── public/        → static assets
```

Path alias: `@/*` maps to `frontend/` root (see `tsconfig.json`).

### Conventions

- **Server Components by default.** Add `'use client'` only when required (interactivity, hooks, browser APIs).
- **All backend communication** goes through `lib/api/` using TanStack Query. No scattered `fetch()` in components.
- **Tailwind** for styling. Avoid CSS modules unless justified.
- **App Router only.** Do not add Pages Router (`pages/`).
- **Turbopack** is the default dev bundler. Do not switch to Webpack without explicit approval.
- **Minimize scope.** No drive-by refactors or unrelated changes.

---

## 4. Backend Coding Rules

### Approved stack

| Technology | Purpose |
|------------|---------|
| FastAPI | HTTP API |
| Python 3.12+ | Runtime (do not target Python 3.11) |
| LangGraph | Multi-agent orchestration |
| Pydantic v2 | Request / response schemas |

### Proposed structure (when scaffolded)

```
backend/
├── app/
│   ├── main.py           → FastAPI app factory
│   ├── api/routes/       → HTTP endpoints
│   ├── agents/           → LangGraph graphs and agent nodes
│   ├── services/         → LLM, Supabase, GitHub, Docker clients
│   ├── models/           → Pydantic schemas
│   └── core/             → config, dependencies, logging
├── tests/
└── requirements.txt      (or pyproject.toml)
```

### Conventions

- **Routes are thin** — delegate to services and agents.
- **Secrets** come from environment variables only. Never hardcode credentials.
- **LLM provider chain:** Gemini (primary) → Groq (secondary) → Ollama (local fallback).
- **Structured logging** on all agent steps.
- **Type hints** on all public functions.
- **API versioning prefix:** `/api/v1/`
- **async-first** for I/O-bound operations.

---

## 5. AI Agent Design Principles

- Each agent has a **single responsibility** (e.g. planner, coder, reviewer).
- **LangGraph** manages state transitions. No ad-hoc agent chaining in route handlers.
- Agent state is **serializable** and persisted where needed (Supabase).
- Agent outputs to downstream agents are **structured** (JSON / Pydantic), not free-form prose.
- **Human-in-the-loop** checkpoints for destructive actions (git push, sandbox file writes).
- **Token / cost awareness:** prefer smaller models for simple tasks.
- **Provider fallback:** Gemini → Groq → Ollama.
- **Embeddings** via pgvector in Supabase — not in the frontend.
- Never expose raw LLM API keys or agent system prompts to the client.

---

## 6. Dependency Management Rules

### Frontend (`frontend/package.json`)

- Pin major framework versions (`next`, `react`) exactly.
- Add shadcn/ui, Zustand, and TanStack Query only when implementing features that need them.
- No upgrades or downgrades without a stated reason and explicit approval.
- Package manager: **npm** (`package-lock.json`).

### Backend (when created)

- Pin versions in `requirements.txt` or `pyproject.toml`.
- Separate dev dependencies from production.
- No frontend packages in backend. No Python in frontend.

### Shared

- No root-level dependency hoisting until workspace tooling is explicitly added.
- Document new dependencies in the commit message and in `docs/` when they affect architecture.

---

## 7. Git and Commit Conventions

### Branching

- `main` → stable
- `feature/<area>-<description>` → e.g. `feature/frontend-shadcn-setup`

### Commits

- **Conventional Commits:** `feat:`, `fix:`, `chore:`, `docs:`, `refactor:`
- Optional scope: `feat(frontend): add shadcn button component`
- One logical change per commit.
- **Never commit:** `.env`, credentials, `node_modules`, `.next`, `__pycache__`

### Pull requests

- Small, reviewable PRs per layer (frontend / backend / infra).
- No cross-cutting mega-PRs in Phase 1.

---

## 8. Code Quality Standards

### General

- Analyze first. Explain before modifying. Use minimal diffs.
- No unnecessary abstractions or premature optimization.
- Match existing conventions in each package.
- Comments only for non-obvious business or technical decisions.

### Frontend

- ESLint (`eslint-config-next`) must pass.
- TypeScript strict mode (enabled in `tsconfig.json`).
- Keep components under ~200 lines; extract when larger.

### Backend

- Use ruff or black + mypy (to be added with backend scaffold).
- pytest for agent logic and API routes.
- All endpoints have Pydantic input and output schemas.

### Security

- Supabase RLS enforced on all tables.
- Auth tokens validated server-side.
- Docker sandbox runs with minimal privileges.
- No secrets in logs or in agent outputs returned to the client.

---

## 9. Phase Guardrails

**Current phase:** Phase 1 — Foundation Setup.

### Strict rule

**Do not implement features outside the current sprint or phase without explicit approval.** If a task is not part of the active phase or sprint scope, stop and ask before writing code.

### Do not (without explicit approval)

- Rewrite existing working code.
- Add features beyond the current phase or sprint scope.
- Install packages not in the approved stack.
- Create files or folders outside the monorepo layout.
- Migrate the frontend from Option B (`app/` at root) to a `src/` layout.
- Upgrade or downgrade dependencies casually.
- Switch Turbopack to Webpack.
- Create `.env` files with real secrets.

### Do

- Analyze first, propose changes, and wait for approval when scope is unclear.
- Keep frontend and backend independently runnable.
- Document architectural decisions in `docs/`.
- Follow the monorepo boundaries in Section 2.

---

## 10. Approved Technology Reference

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 16, TypeScript, Tailwind CSS, shadcn/ui, Zustand, TanStack Query |
| Backend | FastAPI, Python 3.12+, LangGraph |
| LLMs | Google Gemini (primary), Groq (secondary), Ollama (local fallback) |
| Database | Supabase PostgreSQL, pgvector |
| Services | Supabase Storage, Supabase Auth, GitHub API, Docker sandbox |

---

*Last updated: Phase 1 — Foundation Setup*
