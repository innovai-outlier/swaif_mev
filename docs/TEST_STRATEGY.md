# Test Strategy

## Backend (`services/api/tests`)
- `test_auth.py`: login, token-auth `/me`, and admin-only user management.
- `test_enrollments.py`: enrollment creation, cancellation/reactivation, and missing program validation.
- `test_check_ins.py`: check-in write path, points ledger side-effects, streak updates, and duplicate prevention.
- `test_admin_routes.py`: admin program CRUD controls and reward-config bootstrapping.
- `test_migration_compatibility.py`: schema bootstrap and index compatibility checks for fresh installs and existing datasets.

Coverage is enforced through `services/api/pytest.ini` with `pytest-cov` and a fail-under threshold.

## Frontend (`services/web`)
- Vitest runner configured in `vitest.config.ts`.
- `services/web/tests/api.test.ts` verifies:
  - bearer token injection from `localStorage`
  - `204 No Content` responses return `null`
  - API error payload propagation.

Coverage thresholds are enforced in Vitest config.

## Integration Smoke (On-Prem, no Docker)
- `test_onprem_smoke.py` boots on-prem scripts using command overrides to run lightweight local processes.
- Validates service orchestration, API + Web health checks, SQLite write path (DB), and Redis availability (`PING`).
- Does not depend on Docker; only requires local binaries.

## Installer Validation
- `test_installer_validation.py` covers bootstrap/config generation, startup, status checks, shutdown, and uninstall-style cleanup.

## CI Gates
Defined in `.github/workflows/ci.yml`:
1. **lint** (`ruff`, `npm run lint`)
2. **unit** (`pytest -m "not integration and not installer"`, `npm test`)
3. **integration** (`pytest -m integration` with Redis service)
4. **installer** (`pytest -m installer`)

Regression protection is enforced with explicit coverage thresholds in backend and frontend test runners.
