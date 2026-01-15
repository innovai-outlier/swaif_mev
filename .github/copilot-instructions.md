# Motor Clínico (MEV) - AI Coding Agent Guide

## Project Overview
Lifestyle medicine gamification platform (MVP) built as a monorepo with Docker-based services. Focus: habit adherence through programs, check-ins, points, streaks, and badges.

## Architecture (3-Service Stack)

- **services/api**: FastAPI REST API (port 8000) - only service that accesses database
- **services/worker**: Async background jobs (streaks, badges, reminders, routines)
- **services/web**: Next.js UI (port 3000) for patient and admin interfaces
- **infra/compose**: Docker Compose orchestration with Postgres + Redis
- **scripts/**: Operational commands (bootstrap, up, down, migrate, seed, reset)

**Key principle**: Containers are stateless. All state lives in Postgres, Redis, or external storage. Web never accesses DB directly—always through API.

## Essential Workflows

### First-time Setup
```bash
./scripts/bootstrap.sh  # Copies .env.example → .env, validates Docker
./scripts/up.sh         # Builds and starts all services
./scripts/health.sh     # Verifies API/Web are responding
./scripts/migrate.sh    # Runs Alembic migrations (if needed)
./scripts/seed.sh       # Populates initial data
```

### Daily Development
- **Logs**: `./scripts/logs.sh` (tails last 200 lines, follows)
- **Rebuild**: `./scripts/up.sh` (includes --build)
- **Database reset**: `./scripts/reset.sh` (destroys volumes—use carefully)
- **Tests**: `./scripts/test_api.sh` (runs pytest in api container)

### VSCode Tasks
Use Run Task (`Ctrl+Shift+P` → "Tasks: Run Task") for:
- `MC: Up (Docker)`, `MC: Down (Docker)`, `MC: Logs (Docker)`
- `MC: Migrate (API)`, `MC: Seed (API)`, `MC: Reset (DB volumes!)`

## Code Conventions

### Python (API/Worker)
- **Formatting**: Black with `--line-length 100`, isort with `--profile black`
- **Data validation**: Pydantic schemas for all request/response
- **Database**: SQLAlchemy 2 + Alembic for migrations
- **Logging**: stdout only (JSON preferred for production)
- **API versioning**: All endpoints under `/api/v1/...`

### JavaScript/TypeScript (Web)
- **Prettier**: 100 char width, single quotes
- **API calls**: Use `NEXT_PUBLIC_API_BASE_URL` from env (defaults to `http://localhost:8000`)
- **Rule**: No business logic in frontend—keep it thin, consume API

### Environment
Config lives in `infra/compose/.env` (copied from `.env.example`). Key vars:
- `DATABASE_URL`: postgresql+psycopg://mevuser:mevpass@db:5432/mevdb
- `REDIS_URL`: redis://redis:6379
- `NEXT_PUBLIC_API_BASE_URL`: http://localhost:8000

## Data Model (Canonical Entities)
- **Program**: Gamification program container
- **Habit**: Trackable behavior within a program
- **Enrollment**: User participation in a program
- **CheckIn**: Daily habit completion record
- **PointsLedger**: Event-sourced point transactions (never mutate a total column)
- **Badge**: Achievement awarded to users
- **NotificationEvent**: Behavioral events for analytics
- **Streak**: Consecutive days of habit/program completion

## Critical Patterns

### Event-Sourced Points
Points are stored as ledger entries (event-sourced), not mutable totals. Always append new transactions instead of updating a balance.

### Behavioral Analytics
All significant user actions should be loggable to a `NotificationEvent` or analytics table for future insights.

### Service Boundaries
- API is the single source of truth for data operations
- Worker handles async tasks triggered by API or scheduled jobs
- Web is presentation layer only—delegates all logic to API

## Docker Context
- Build context is always repository root (see Dockerfiles: `context: ../../`)
- Services reference each other by service name (e.g., `db:5432`, `redis:6379`)
- Health checks ensure DB is ready before API starts (see `depends_on` in docker-compose.yml)

## References
- **Architecture overview**: `COPILOT_CONTEXT.md`
- **Dev setup**: `docs/DEV_SETUP.md`
- **Service definitions**: `infra/compose/docker-compose.yml`
- **EditorConfig**: Python 4-space indent, JS/TS/YAML 2-space
