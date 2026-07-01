# FastAPI Modular Monolith Starter

An advanced, batteries-included starter for building **modular monoliths** with
FastAPI — async end-to-end, feature-sliced, and designed so adding a new module
is a one-command operation.

It fuses two influences:

- the layered, async, JWT-secured billing service (SQLModel + asyncpg + Alembic
  + APScheduler), and
- the [arctikant modular-monolith kit](https://github.com/arctikant/fastapi-modular-monolith-starter-kit)
  (module-per-feature, repository pattern, gateways, event bus).

…and removes their main pain points: **no hand-wiring routers**, and a
**module generator** so new features are scaffolded, wired, and migration-ready
in seconds.

---

## Why this layout

Instead of splitting by technical layer at the top level
(`controllers/`, `services/`, `models/` …), the app is split by **feature
module**. Each module is a vertical slice that owns its models, schemas,
repository, service, routes, events and public gateway:

```
app/
├── main.py                 # app factory + lifespan (auto-registers modules)
├── cli/                    # `python -m app.cli` — module generator & introspection
├── core/                   # shared infrastructure (see below)
└── modules/
    ├── auth/               # users, register/login/refresh, JWT deps, gateway
    │   ├── __init__.py     # ← public surface + `module = Module(...)`
    │   ├── models.py
    │   ├── schemas.py
    │   ├── repository.py
    │   ├── service.py
    │   ├── dependencies.py # CurrentUser / AdminUser
    │   ├── gateway.py      # sync cross-module access
    │   ├── events.py       # UserRegistered / UserDeleted
    │   ├── listeners.py
    │   ├── seed.py         # bootstrap admin
    │   └── routes/v1/
    └── items/              # example owner-scoped CRUD (copy me)
```

### Core infrastructure (`app/core/`)

| File | Responsibility |
|------|----------------|
| `config.py` | Pydantic settings from `.env` (`get_settings()`) |
| `database.py` | Async engine, session factory, `get_session` dependency |
| `models.py` | `BaseModel` (UUID + timestamps), `SoftDeleteMixin` |
| `repository.py` | `BaseRepository` — CRUD + pagination + soft-delete |
| `schemas.py` | `BaseSchema` DTO base |
| `pagination.py` | `PageParams` dependency, `Page[T]` response |
| `security.py` | bcrypt hashing + JWT access/refresh encode/decode |
| `exceptions.py` / `handlers.py` | Domain errors → uniform JSON envelope |
| `events.py` | In-process async event bus (`@on`, `event_bus.emit`) |
| `cache.py` | Redis-or-in-memory cache + `@cached` decorator |
| `scheduler.py` | APScheduler wrapper (`@scheduled`) |
| `middleware.py` | CORS + request-id + timing |
| `logging.py` | structlog setup |
| `module.py` | `Module` type + auto-discovery |

---

## Quick start

```bash
# 1. Install (uv recommended)
uv venv && uv pip install -e ".[dev]"      # or: pip install -e ".[dev]"
cp .env.example .env

# 2. Run — works immediately on SQLite, no infra needed
make run                                    # uvicorn app.main:app --reload

# 3. Open the docs
open http://localhost:8000/api/v1/docs
```

Run the test suite (SQLite, zero infra):

```bash
make test
```

### With Postgres + Redis

```bash
docker compose up --build
```

---

## Add a feature module in one command

```bash
python -m app.cli new-module product      # or: make module name=product
```

This scaffolds `app/modules/products/` with a `Product` model, schemas,
repository, service, and a full CRUD router — **already auto-registered**. Then:

```bash
alembic revision --autogenerate -m "add products"
alembic upgrade head
```

That's it. No router imports to edit, no metadata to register. Inspect what got
wired:

```bash
python -m app.cli list-modules
python -m app.cli routes
```

---

## Key patterns

**Auto-discovery.** `discover_modules()` scans `app/modules/*`, imports each
package (registering its models & listeners), and the app factory includes every
module's router under `/api/<version>`.

**Repository + Service.** Routes stay thin. Services own the unit of work
(they `commit()` explicitly; `get_session` provides a safety-net
commit/rollback) and compose repositories. `BaseRepository` gives typed CRUD,
`paginate()`, and transparent soft-delete.

**Cross-module communication.**
- *Synchronous* → **Gateway**: `AuthGateway(session).get_user(id)` returns a
  `PublicUser` DTO. Modules never import each other's ORM models.
- *Asynchronous* → **Event bus**: auth emits `UserRegistered`; the items module
  reacts in `listeners.py` (creates a welcome item) without either importing the
  other's internals.

**Auth.** JWT HS256 with separate access/refresh tokens. Refresh tokens carry no
identity claims and are rejected everywhere except `/auth/refresh`. Dependencies
`CurrentUser` / `AdminUser` guard routes.

**Anti-IDOR.** Owner-scoped services filter by the caller's id and return
**404** (not 403) for resources owned by someone else — existence is never
leaked. See `items/service.py`.

**Uniform errors.** Raise `NotFoundError`, `ConflictError`, … from services;
handlers emit `{"error": {"code", "message", "details"}}`.

---

## Common commands

```bash
make run           # dev server (reload)
make test          # pytest
make lint format   # ruff
make typecheck     # mypy
make migrate                       # alembic upgrade head
make makemigration m="add x"       # autogenerate a revision
make module name=order             # scaffold a module
make up / make down                # docker compose stack
```

See `CLAUDE.md` for architecture guidance aimed at AI coding assistants.
