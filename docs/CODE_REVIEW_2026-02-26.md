# Deep Code Review (2026-02-26)

## Scope
- Backend: `services/api/app`
- Frontend: `services/web`
- Infrastructure/test scripts under `scripts/`

## Coverage/Test execution results
1. API coverage command (`pytest --cov`) cannot run meaningful coverage because there are no repository test files under `services/api`.
2. Web test command (`npm test`) is not configured in `services/web/package.json`.
3. Performed quality gates that are available (`next lint`, `next build`, Python compilation checks).

## Confirmed defect fixed in this branch
### 1) Frontend API client crashed on `204 No Content`
- **Where:** `services/web/lib/api.ts`
- **Impact:** `cancelEnrollment()` calls DELETE endpoint `/api/v1/enrollments/{id}/`, which returns HTTP 204. `fetchAPI` always attempted `response.json()`, which throws on empty body.
- **Fix:** Added explicit `response.status === 204` handling returning `null`.

### 2) Missing auth propagation in frontend API client
- **Where:** `services/web/lib/api.ts`
- **Impact:** Authenticated endpoints fail unless each caller manually sets bearer token.
- **Fix:** Inject `Authorization: Bearer <token>` from `localStorage` on client-side requests.

## Additional high-priority issues found (proposed fixes)
1. **Hardcoded JWT secret key (security risk)**
   - File: `services/api/app/auth.py`
   - Proposed fix: Load `SECRET_KEY` from environment and fail fast if missing in non-local env.

2. **Insufficient automated test coverage in repo**
   - Files: no first-party `tests/` package currently present.
   - Proposed fix: add backend tests (auth/check-ins/enrollments) and frontend unit tests around API client behavior, including 204 handling and token headers.

3. **Login page bypasses shared API client + env config**
   - File: `services/web/app/login/page.tsx`
   - Proposed fix: use `NEXT_PUBLIC_API_BASE_URL` consistently and centralize auth calls in `lib/api.ts`.

4. **No explicit constraints on pagination query parameters**
   - Files: multiple routers (e.g., `check_ins.py`, `enrollments.py`)
   - Proposed fix: enforce bounds (`skip >= 0`, `1 <= limit <= 200`) to reduce accidental high-load queries.

## Suggested next sprint actions
- Add `pytest-cov` and a baseline test suite with branch protection threshold.
- Add frontend test runner (`vitest` or `jest`) and API client tests.
- Introduce centralized settings module for API secrets and env handling.
