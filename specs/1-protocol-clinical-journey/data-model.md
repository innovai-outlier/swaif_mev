# Data Model: Protocol Clinical Journey

## New SQLAlchemy Models

### ProtocolTemplate
- id (int, PK)
- code (string, unique)
- name (string)
- version (string)
- description (text)
- is_active (bool)
- default_program_id (nullable FK → programs.id)
- created_at (datetime)
- updated_at (datetime)

### ProtocolPhase
- id (int, PK)
- protocol_template_id (FK)
- name (string)
- phase_key (string, e.g., triage/baseline/intervene/retest)
- phase_order (int)
- entry_criteria_json (nullable, JSONB)
- exit_criteria_json (nullable, JSONB)

### ArtifactDefinition
- id (int, PK)
- protocol_template_id (FK)
- artifact_key (string, e.g., q_7_functions)
- type (string)
- name (string)
- schema_json (nullable, JSONB)
- scoring_json (nullable, JSONB)

### ProtocolRun
- id (int, PK)
- user_id (int)
- protocol_template_id (FK)
- status (string)
- current_phase_id (nullable FK → protocol_phases.id)
- started_at (datetime)
- completed_at (nullable, datetime)
- created_at (datetime)
- updated_at (datetime)

### ArtifactInstance
- id (int, PK)
- protocol_run_id (FK)
- artifact_definition_id (FK)
- collected_at (datetime)
- payload_json (nullable, JSONB)
- computed_json (nullable, JSONB)
- source (string, nullable: patient/admin/integration)

### InterventionTemplate (optional, recommended)
- id (int, PK)
- protocol_template_id (FK)
- intervention_key (string)
- type (habit|supplement|diet|appointment|task)
- name (string)
- description (string)
- habit_blueprint_json (nullable, JSONB)
- activation_rules_json (nullable, JSONB)

### ProtocolGeneratedItem (optional)
- id (int, PK)
- protocol_run_id (FK)
- intervention_template_id (FK)
- generated_habit_id (nullable FK → habits.id)
- created_at (datetime)

## Changes to Existing Models

### Habit
- source_type (string, default "manual", nullable=False)
- source_ref_id (int, nullable)
- target_metric_key (string, nullable)

### CheckIn
- metric_key (string, nullable)
- value_numeric (Numeric/Float, nullable)
- value_text (Text, nullable)

## Relationships
- ProtocolTemplate → ProtocolPhase, ArtifactDefinition, InterventionTemplate
- ProtocolRun → ArtifactInstance, ProtocolGeneratedItem
- InterventionTemplate → ProtocolGeneratedItem
- Habit, CheckIn: linked via source_type/source_ref_id/target_metric_key

## Validation Rules
- All new fields in existing models must be nullable and defaulted for backwards compatibility.
- JSONB columns preferred for all artifact and computed data.
- Indices:
  - artifact_instances: (protocol_run_id, artifact_definition_id, collected_at desc)
  - protocol_runs: (user_id, status)
  - habits: (program_id, source_type, source_ref_id)
  - check_ins: (user_id, metric_key, check_in_date)
