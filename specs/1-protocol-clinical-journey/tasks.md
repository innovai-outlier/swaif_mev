# Protocol Clinical Journey – Implementation Tasks

<!-- Requirement/Task Mapping Table -->
| Requirement Key | Task IDs | Notes |
|-----------------|----------|-------|
| FR-001          | T034, T035, T036 | Protocol template CRUD/admin UI tasks |
| FR-002          | T010, T011, T014, T015, T037 | Protocol run creation/tracking tasks |
| FR-003          | T018, T019, T022, T039 | Artifact submission/storage tasks |
| FR-004          | T019, T020, T036, T037 | Scoring/priorities tasks |
| FR-005          | T037, T038, T039 | Intervention generation/integration tasks |
| FR-006          | T023, T024, T025, T026, T027, T028, T029, T030 | PointsLedger, Streak, Badges tasks |
| FR-007          | T034, T035, T036, T010, T014, T018 | CRUD endpoints for templates/runs |
| FR-008          | T006, T008, T003 | JSONB persistence tasks |
| FR-009          | T006, T009 | Backwards compatibility tasks |
| FR-010          | T004, T043 | Seed data tasks |
| FR-011          | T043, T045, T046, T047 | Pytest/test coverage tasks |
| FR-012          | T042, T043 | Documentation tasks |
| FR-013          | T023, T027, T038 | Worker/recompute tasks |
| Analytics       | T031, T032, T033 | Explicit mapping for analytics endpoints and dashboards |
| Reminders       | T038, T039 | Explicit mapping for reminder scheduling and display |
| Non-functional  | T044, T006, T008 | Performance, migration, compatibility tasks |

---

## 1. Setup & Foundational Tasks

### Environment & Project Setup
[*] T001 Ensure `.env` and Docker Compose are configured for all services
[*] T002 Run `bootstrap.sh`, `up.sh`, and `health.sh` to verify baseline environment
[*] T003 Apply latest Alembic migrations (`migrate.sh`)
[*] T004 Seed initial data for programs, habits, users (`seed.sh`)
[*] T005 Confirm API, Worker, and Web services are running and healthy

### Data Model Foundation
[*] T006 Review and update SQLAlchemy models for Program, Habit, Enrollment, CheckIn, PointsLedger, Badge, NotificationEvent, Streak
[*] T007 Validate Pydantic schemas for all request/response objects
[*] T008 Ensure event-sourced PointsLedger pattern is implemented (append-only, no mutable totals)
[*] T009 Add/verify NotificationEvent logging for all key user actions

---

## 2. User Story Phase 1: Program Enrollment & Habit Tracking

### US-1: As a patient, I can enroll in a clinical protocol program
- [ ] T010 [US1] Implement API endpoint: `POST /api/v1/enrollments` in services/api/app/routers/enrollments.py
- [ ] T011 [US1] Validate enrollment logic in services/api/app/services/enrollment_service.py
- [ ] T012 [US1] Add frontend enrollment UI in services/web/app/programs/page.tsx
- [ ] T013 [US1] Log NotificationEvent for enrollment in services/api/app/services/notification_service.py

### US-2: As a patient, I can view my enrolled programs and associated habits
- [ ] T014 [US1] Implement API endpoint: `GET /api/v1/enrollments/{user_id}` in services/api/app/routers/enrollments.py
- [ ] T015 [US1] Implement API endpoint: `GET /api/v1/programs/{program_id}/habits` in services/api/app/routers/programs.py
- [ ] T016 [US1] Build frontend dashboard for enrolled programs and habits in services/web/app/programs/page.tsx
- [ ] T017 [US1] Ensure habit metadata is displayed in services/web/app/programs/page.tsx

### US-3: As a patient, I can check in daily for each habit
- [ ] T018 [US1] Implement API endpoint: `POST /api/v1/check-ins` in services/api/app/routers/check_ins.py
- [ ] T019 [US1] Validate check-in logic in services/api/app/services/checkin_service.py
- [ ] T020 [US1] Update PointsLedger on successful check-in in services/api/app/services/points_ledger_service.py
- [ ] T021 [US1] Log NotificationEvent for check-in in services/api/app/services/notification_service.py
- [ ] T022 [US1] Add frontend check-in UI in services/web/app/check-ins/page.tsx

---

## 3. User Story Phase 2: Gamification, Streaks, Badges, Analytics

### US-4: As a patient, I earn points and streaks for daily habit completion
- [ ] T023 [US2] Implement streak calculation logic in services/worker/app/main.py
- [ ] T024 [US2] Update PointsLedger for streak bonuses in services/api/app/services/points_ledger_service.py
- [ ] T025 [US2] Display streaks and points in frontend dashboard in services/web/app/streaks/page.tsx
- [ ] T026 [US2] Log NotificationEvent for streak events in services/api/app/services/notification_service.py

### US-5: As a patient, I receive badges for milestone achievements
- [ ] T027 [US2] Implement badge awarding logic in services/worker/app/main.py
- [ ] T028 [US2] Create API endpoint: `GET /api/v1/badges/{user_id}` in services/api/app/routers/badges.py
- [ ] T029 [US2] Add badge display to frontend in services/web/app/badges/page.tsx
- [ ] T030 [US2] Log NotificationEvent for badge awards in services/api/app/services/notification_service.py

### US-6: As an admin, I can view analytics on program adherence and habit completion
- [ ] T031 [US2] Implement API endpoints for analytics in services/api/app/routers/admin_analytics.py
- [ ] T032 [US2] Build admin analytics dashboard in services/web/app/admin/analytics/page.tsx
- [ ] T033 [US2] Ensure NotificationEvent data is queryable for analytics in services/api/app/services/notification_service.py

---

## 4. User Story Phase 3: Protocol Engine, Templates, Advanced Features

### US-7: As an admin, I can create and manage protocol templates
- [ ] T034 [US3] Implement API endpoints for protocol template CRUD in services/api/app/routers/protocol_templates.py
- [ ] T035 [US3] Build admin UI for protocol template management in services/web/app/admin/programs/page.tsx
- [ ] T036 [US3] Validate template logic in services/api/app/services/protocol_template_service.py

### US-8: As a patient, I can view protocol progress and receive reminders
- [ ] T037 [US3] Implement progress tracking logic in services/api/app/services/protocol_run_service.py
- [ ] T038 [US3] Add reminder scheduling in services/worker/app/main.py
- [ ] T039 [US3] Display progress and reminders in frontend in services/web/app/programs/page.tsx

---

## 5. Polish & QA

### Polish
- [ ] T040 Review UI for accessibility and responsiveness in services/web/app/
- [ ] T041 Add loading, error, and success states to all user flows in services/web/app/
- [ ] T042 Ensure all API responses are validated and documented in services/api/app/
- [ ] T043 Write comprehensive tests (API, Worker, Web) in services/api/tests/, services/web/__tests__/
- [ ] T044 Review and optimize Docker Compose health checks in infra/compose/docker-compose.yml

### QA & Acceptance
- [ ] T045 Map each requirement and acceptance scenario from spec.md to test cases in services/api/tests/, services/web/__tests__/
- [ ] T046 Validate all user stories against acceptance criteria in services/api/tests/, services/web/__tests__/
- [ ] T047 Perform end-to-end testing of enrollment, check-ins, gamification, analytics in services/api/tests/, services/web/__tests__/

---

## 6. Dependencies & Parallel Execution

### Dependencies
- Data model tasks must be completed before API and Worker logic
- API endpoints must be available before frontend integration
- NotificationEvent logging is required for analytics and reminders
- Worker service must be running for streaks, badges, reminders
- Analytics endpoints (T031, T032, T033) and reminder scheduling (T038, T039) are explicitly mapped to requirements FR-006, FR-013, and non-functional coverage.

### Parallel Execution Examples
- Frontend UI for enrollment, check-ins, and dashboard can be developed in parallel with API endpoint implementation (using mock data)
- Worker logic for streaks and badges can be developed in parallel with PointsLedger and NotificationEvent integration
- Admin analytics dashboard can be built in parallel with NotificationEvent logging and API analytics endpoints
- Analytics and reminder features can be developed in parallel with core protocol run logic, maintaining terminology consistency for "protocol run" throughout.

---

## 7. Implementation Strategy

- Start with foundational setup and data model validation
- Implement API endpoints and core business logic (event-sourced, stateless)
- Develop frontend UI in parallel, using API mocks where needed
- Integrate Worker service for async gamification logic
- Ensure all user actions are logged for analytics and reminders
- Map every requirement and acceptance scenario to a testable task
- Maintain consistent terminology for "protocol run" across all code, docs, and UI
- Polish UI/UX and validate with end-to-end tests before release

---

## 8. Checklist Summary (Quick Reference)

- [ ] Environment setup complete
- [ ] Data models and schemas validated
- [ ] API endpoints implemented
- [ ] Frontend UI built and integrated
- [ ] Worker service logic for streaks, badges, reminders
- [ ] NotificationEvent logging for all key actions
- [ ] Analytics endpoints and dashboards
- [ ] Protocol templates and advanced features
- [ ] Polish, QA, and acceptance testing

---

**References:**
- [specs/1-protocol-clinical-journey/plan.md](specs/1-protocol-clinical-journey/plan.md)
- [specs/1-protocol-clinical-journey/spec.md](specs/1-protocol-clinical-journey/spec.md)
- [COPILOT_CONTEXT.md](COPILOT_CONTEXT.md)
- [docs/DEV_SETUP.md](docs/DEV_SETUP.md)
