# Technical Plan: Protocol Clinical Journey

**Feature Branch**: `1-protocol-clinical-journey`
**Spec**: [spec.md](./spec.md)
**Created**: 2026-02-28
**Status**: Draft

## Architecture Overview
- FastAPI backend (services/api) with SQLAlchemy 2, Alembic, Pydantic
- PostgreSQL (JSONB for artifact data), Redis for async jobs
- Next.js frontend (services/web) for admin/clinic UI
- Celery worker (services/worker) for protocol run recompute (optional)
- Docker Compose orchestration

## Data Model Changes
- Add new models: ProtocolTemplate, ProtocolPhase, ArtifactDefinition, ProtocolRun, ArtifactInstance, InterventionTemplate, ProtocolGeneratedItem
- Update Habit and CheckIn models for protocol linkage and metrics
- All new fields in existing models are nullable/defaulted for backwards compatibility
- Use JSONB columns for all artifact/computed data

## API Endpoints
- /admin/protocol-templates (CRUD, seed)
- /protocol-runs (start, get, submit artifact, generate interventions, advance phase, timeline)
- All endpoints under /api/v1/
- Pydantic schemas for all request/response

## Migration Plan
- Alembic migrations for new tables and columns
- Indices for artifact_instances, protocol_runs, habits, check_ins
- Backwards-compatible changes only

## Integration Points
- MEV engine: Habits, CheckIns, PointsLedger, Streak, Badges
- Worker: recompute_protocol_run task (optional)
- NotificationEvent for analytics

## Testing Plan
- Pytest for API: template creation, protocol run, artifact submission, intervention generation, phase advancement
- Vitest for web: admin/clinic UI flows (optional)
- Seed script for "young_forever_core_v1" protocol

## Documentation
- Update COPILOT_CONTEXT.md and docs/ with new domain and usage

## Implementation Phases
1. Map existing CRUD/router patterns and DB session/auth handling
2. Implement new models and relationships
3. Create Alembic migrations
4. Implement Pydantic schemas
5. Build routers/services for protocol flows
6. Seed protocol and interventions
7. Add tests for all main flows
8. (Optional) Worker and web admin UI

## Risks & Mitigations
- **Risk:** Breaking existing MEV features. **Mitigation:** All changes are backwards-compatible, tested with legacy data.
- **Risk:** Performance with large artifact data. **Mitigation:** Use JSONB and indices, test with sample data.
- **Risk:** MEV integration failures. **Mitigation:** Error logging, notifications, retry logic.

## Stage Gate Checklist
- [x] Simplicity: Architecture and flows explained in plain language
- [x] Anti-Abstraction: No unnecessary layers; all abstractions justified
- [x] Integration-First: API contracts and integration flows defined before implementation
- [x] Traceability: All requirements mapped to plan phases and tasks

## Next Steps
- Generate tasks.md mapping all requirements and plan phases to actionable tasks
- Review plan with stakeholders and update as needed
