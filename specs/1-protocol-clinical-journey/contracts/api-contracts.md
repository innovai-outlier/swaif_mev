# API Contracts: Protocol Clinical Journey

## Protocol Templates (Admin)
- `GET /admin/protocol-templates` — List all protocol templates
- `POST /admin/protocol-templates` — Create new protocol template
- `GET /admin/protocol-templates/{id}` — Get protocol template by ID
- `PUT /admin/protocol-templates/{id}` — Update protocol template
- `POST /admin/protocol-templates/{id}/seed-young-forever` — Seed template (optional)

## Protocol Runs
- `POST /protocol-runs` — Start protocol run for user_id + template_code
- `GET /protocol-runs/{id}` — Get protocol run by ID
- `POST /protocol-runs/{id}/artifacts/{artifact_key}` — Submit artifact instance
- `POST /protocol-runs/{id}/generate-interventions` — Generate interventions (habits/check-ins)
- `POST /protocol-runs/{id}/advance-phase` — Advance protocol phase
- `GET /protocol-runs/{id}/timeline` — Get run timeline (phases, artifacts, interventions)

## Integration
- All endpoints return Pydantic schemas for request/response validation
- All new endpoints under `/api/v1/` namespace
- All business logic in API, not frontend

## Backwards Compatibility
- Existing endpoints for Program, Habit, CheckIn, PointsLedger, Streak, Badge remain unchanged
- New fields in Habit/CheckIn are nullable/defaulted
