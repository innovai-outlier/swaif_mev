# Feature Specification: Protocol Clinical Journey

**Feature Branch**: `1-protocol-clinical-journey`
**Created**: 2026-02-28
**Status**: Draft
**Input**: User description: "PLANEJAR e IMPLEMENTAR nova versão do Motor Clínico MVP/MEV para suportar jornada clínica baseada no livro Jovem Para Sempre (Parte III), mantendo compatibilidade com o que já existe."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create and Manage Protocol Templates (Priority: P1)
Admin users can create, update, and manage clinical protocol templates with ordered phases and artifact definitions.

**Why this priority**: Enables the foundation for protocol-driven clinical journeys, essential for all subsequent flows.

**Independent Test**: Can be fully tested by creating a new protocol template, adding phases and artifacts, and verifying persistence and retrieval.

**Acceptance Scenarios**:
1. **Given** no protocol templates exist, **When** an admin creates a new template, **Then** the template is available for selection and editing.
2. **Given** a protocol template exists, **When** an admin updates phases or artifacts, **Then** changes are reflected in subsequent protocol runs.

---

### User Story 2 - Start and Execute Protocol Run for Patient (Priority: P2)
Clinic/admin users can start a protocol run for a patient, submit artifacts (questionnaire, labs, wearables), and advance through protocol phases.

**Why this priority**: Delivers the core clinical workflow for patients, enabling structured data collection and phase progression.

**Independent Test**: Can be tested by starting a protocol run, submitting artifacts, and advancing phases, verifying correct state transitions and data storage.

**Acceptance Scenarios**:
1. **Given** a protocol template exists, **When** a protocol run is started for a patient, **Then** the run is tracked and phases are available.
2. **Given** a protocol run in a phase, **When** required artifacts are submitted, **Then** the system computes scores and allows phase advancement.

---

### User Story 3 - Generate Interventions and Integrate with MEV (Priority: P3)
System generates personalized interventions (habits, check-ins) based on protocol priorities and integrates them with the existing MEV engine.

**Why this priority**: Connects protocol logic to habit formation and tracking, ensuring clinical impact and continuity with MEV.

**Independent Test**: Can be tested by generating interventions for a protocol run and verifying habits/check-ins are created and tracked in MEV.

**Acceptance Scenarios**:
1. **Given** a protocol run with computed priorities, **When** interventions are generated, **Then** habits and check-ins are created in the MEV system.
2. **Given** a patient completes a protocol milestone, **When** points and badges are awarded, **Then** event-sourcing and streaks remain functional.

---

### Edge Cases & Measurable Outcomes
- If a protocol phase is missing required artifacts, phase advancement is blocked and a notification is sent to the responsible admin/clinic user. **Test:** Attempt to advance phase without required artifacts; verify error and notification.
- On duplicate artifact submissions, only the latest instance is used for scoring, but all are stored for audit. **Test:** Submit multiple artifacts for same key; verify audit log and scoring uses latest.
- If MEV integration fails during intervention generation, system logs the error, notifies admin, and allows retry. **Test:** Simulate MEV failure; verify error log, notification, and retry path.
- For backwards compatibility, new fields in Habit/CheckIn are nullable and defaulted. **Test:** Create legacy and new records; verify no errors and correct defaults.

## Requirements *(mandatory)*

### Functional Requirements
- **FR-001**: System MUST allow admin users to create, update, and manage protocol templates with phases and artifact definitions.
- **FR-002**: System MUST allow clinic/admin users to start protocol runs for patients and track phase progression.
- **FR-003**: System MUST allow submission and storage of artifact instances (questionnaire, labs, wearables) per protocol run.
- **FR-004**: System MUST compute scores and priorities from submitted artifacts and store results.
- **FR-005**: System MUST generate interventions (habits, check-ins) based on protocol priorities and integrate with MEV engine.
- **FR-006**: System MUST ensure PointsLedger, Streak, and Badges remain functional and can award protocol milestones.
- **FR-007**: System MUST support CRUD operations for protocol templates and protocol runs via API endpoints.
- **FR-008**: System MUST persist artifact data using Postgres JSONB columns wherever possible; fallback to serialized JSON text only if JSONB is not available in the current stack. This ensures optimal query performance, indexing, and future-proofing for analytics.
- **FR-009**: System MUST maintain backwards compatibility for existing Habit and CheckIn models (nullable fields, defaults).
- **FR-010**: System MUST provide seed data for "young_forever_core_v1" protocol and interventions.
- **FR-011**: System MUST provide pytest tests for main protocol flows (template creation, protocol run, artifact submission, intervention generation, phase advancement).
- **FR-012**: System MUST document the new "Protocolos" domain and integration points with MEV.
- **FR-013**: System MUST allow optional worker task to recompute protocol run scores (Celery placeholder).

### Key Entities
- **ProtocolTemplate**: Represents a versioned clinical protocol, with phases and artifact definitions.
- **ProtocolPhase**: Ordered step in a protocol template, with entry/exit criteria.
- **ArtifactDefinition**: Defines a data collection artifact (questionnaire, lab panel, wearable metric) for a protocol.
- **ProtocolRun**: Instance of a protocol execution for a patient, tracking current phase and status.
- **ArtifactInstance**: Collected data for a specific artifact in a protocol run, including payload and computed results.
- **InterventionTemplate**: Blueprint for generating habits, supplements, or other interventions based on protocol priorities.
- **ProtocolGeneratedItem**: Record of generated habits/interventions for a protocol run.
- **Habit**: Trackable behavior, now with source_type/source_ref_id/target_metric_key for protocol linkage.
- **CheckIn**: Daily record, now supporting metric_key/value_numeric/value_text for protocol metrics.

## Success Criteria *(mandatory)*

### Measurable Outcomes
- **SC-001**: Admins can create and manage protocol templates and phases in under 5 minutes per template.
- **SC-002**: Clinics can start and execute protocol runs for patients, with phase progression and artifact submission, without errors.
- **SC-003**: Interventions generated from protocol priorities are correctly created as habits/check-ins and tracked in MEV.
- **SC-004**: All protocol milestones (triage, baseline, retest) award points and badges, with event-sourcing and streaks remaining functional.
- **SC-005**: System maintains backwards compatibility for all existing MEV features (no data loss or breakage).
- **SC-006**: Protocol flows are covered by automated pytest tests, passing in CI.
- **SC-007**: Documentation for "Protocolos" domain is updated and understandable by clinical/admin users.

## Assumptions
- Artifact data MUST be persisted using Postgres JSONB columns wherever possible; fallback to serialized JSON text only if JSONB is not available in the current stack. This ensures optimal query performance, indexing, and future-proofing for analytics.
- Existing MEV models (Program, Habit, CheckIn, PointsLedger, Streak, Badge) are stable and must not be broken.
- Worker automation is optional; placeholder task is sufficient for MVP.
- Web admin interface is optional for MVP; focus is on API and backend flows.

## Clarifications
### Session 2026-02-28
- Q: Should artifact data be persisted using Postgres JSONB columns or always as serialized JSON text? → A: Use Postgres JSONB columns for artifact data (preferred; fallback to text if unavailable)
