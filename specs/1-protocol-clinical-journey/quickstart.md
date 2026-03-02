# Quickstart: Protocol Clinical Journey

## Setup
1. Ensure Docker and Docker Compose are installed
2. Run `./scripts/bootstrap.sh` to set up environment
3. Run `./scripts/up.sh` to start all services
4. Run `./scripts/migrate.sh` to apply Alembic migrations
5. Run `./scripts/seed.sh` to populate initial and protocol seed data

## Development
- API: FastAPI at http://localhost:8000
- Web: Next.js at http://localhost:3000
- Worker: Celery (optional, for recompute tasks)

## Testing
- Run `./scripts/test_api.sh` for API tests (pytest)
- Run `./scripts/test_web.sh` for web tests (Vitest)

## Feature Usage
- Create protocol templates via admin endpoints
- Start protocol runs for patients
- Submit artifacts and generate interventions
- Advance protocol phases and track timeline

## Documentation
- See [COPILOT_CONTEXT.md](../../COPILOT_CONTEXT.md) and [spec.md](./spec.md) for domain details
