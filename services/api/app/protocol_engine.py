"""Domain helpers for protocol templates and runs."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models import (
    ArtifactDefinition,
    ArtifactInstance,
    Enrollment,
    Habit,
    InterventionTemplate,
    PointsLedger,
    Program,
    ProtocolGeneratedItem,
    ProtocolPhase,
    ProtocolRun,
    RewardConfig,
)


MILESTONE_DEFAULT_POINTS = {
    "triage": 25,
    "baseline": 50,
    "retest": 75,
}


def compute_artifact_scores(artifact_key: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Compute domain-specific derived values for known artifact types."""
    if artifact_key != "q_7_functions":
        return {}

    responses = payload.get("responses", {})
    if not isinstance(responses, dict):
        return {}

    function_scores: Dict[str, float] = {}
    for function_key, value in responses.items():
        if isinstance(value, bool):
            function_scores[function_key] = 1.0 if value else 0.0
        elif isinstance(value, (int, float)):
            function_scores[function_key] = float(value)

    if not function_scores:
        return {}

    sorted_scores = sorted(function_scores.items(), key=lambda item: item[1], reverse=True)
    top_function, top_score = sorted_scores[0]

    return {
        "function_scores": function_scores,
        "top_function": top_function,
        "top_score": top_score,
        "ranked_functions": sorted_scores,
    }


def ensure_program_for_run(db: Session, run: ProtocolRun) -> Program:
    """Get or create target program for generated interventions."""
    template = run.protocol_template
    if template.default_program_id:
        program = db.query(Program).filter(Program.id == template.default_program_id).first()
        if program:
            return program

    program_name = f"Protocolo {template.name} - Paciente {run.user_id}"
    program = (
        db.query(Program)
        .filter(Program.name == program_name)
        .order_by(Program.id.desc())
        .first()
    )
    if not program:
        program = Program(name=program_name, description=f"Programa auto-gerado para run {run.id}")
        db.add(program)
        db.flush()

    enrollment = (
        db.query(Enrollment)
        .filter(Enrollment.user_id == run.user_id, Enrollment.program_id == program.id)
        .first()
    )
    if not enrollment:
        db.add(Enrollment(user_id=run.user_id, program_id=program.id, is_active=True))

    return program


def _rule_matches(rule: Optional[Dict[str, Any]], context: Dict[str, Any]) -> bool:
    if not rule:
        return True
    target = rule.get("top_function")
    if not target:
        return True
    return target == context.get("top_function")


def generate_habits_from_interventions(db: Session, run: ProtocolRun) -> List[int]:
    """Generate habits for a protocol run using intervention templates and priorities."""
    latest_triage = (
        db.query(ArtifactInstance)
        .join(ArtifactDefinition, ArtifactDefinition.id == ArtifactInstance.artifact_definition_id)
        .filter(
            ArtifactInstance.protocol_run_id == run.id,
            ArtifactDefinition.artifact_key == "q_7_functions",
        )
        .order_by(ArtifactInstance.collected_at.desc())
        .first()
    )
    context = latest_triage.computed_json if latest_triage and latest_triage.computed_json else {}

    program = ensure_program_for_run(db, run)
    templates = (
        db.query(InterventionTemplate)
        .filter(InterventionTemplate.protocol_template_id == run.protocol_template_id)
        .all()
    )

    generated_habits: List[int] = []
    for template in templates:
        if template.type != "habit":
            continue
        rules = template.activation_rules_json or {}
        if not _rule_matches(rules, context):
            continue

        exists = (
            db.query(ProtocolGeneratedItem)
            .filter(
                ProtocolGeneratedItem.protocol_run_id == run.id,
                ProtocolGeneratedItem.intervention_template_id == template.id,
            )
            .first()
        )
        if exists:
            if exists.generated_habit_id:
                generated_habits.append(exists.generated_habit_id)
            continue

        blueprint = template.habit_blueprint_json or {}
        habit = Habit(
            program_id=program.id,
            name=template.name,
            description=template.description,
            points_per_completion=blueprint.get("points_per_completion", 10),
            source_type="protocol",
            source_ref_id=run.id,
            target_metric_key=blueprint.get("target_metric_key"),
            is_active=True,
        )
        db.add(habit)
        db.flush()

        db.add(
            ProtocolGeneratedItem(
                protocol_run_id=run.id,
                intervention_template_id=template.id,
                generated_habit_id=habit.id,
            )
        )
        generated_habits.append(habit.id)

    return generated_habits


def award_protocol_milestone(db: Session, run: ProtocolRun, milestone_key: str) -> None:
    """Add points for protocol milestones if not already awarded."""
    event_type = "protocol_milestone"
    description = f"Milestone de protocolo: {milestone_key}"

    exists = (
        db.query(PointsLedger)
        .filter(
            PointsLedger.user_id == run.user_id,
            PointsLedger.event_type == event_type,
            PointsLedger.description == description,
            PointsLedger.event_reference_id == run.id,
        )
        .first()
    )
    if exists:
        return

    config_key = f"protocol_milestone_{milestone_key}_points"
    config = db.query(RewardConfig).filter(RewardConfig.config_key == config_key).first()
    points = config.config_value if config else MILESTONE_DEFAULT_POINTS.get(milestone_key, 20)
    db.add(
        PointsLedger(
            user_id=run.user_id,
            program_id=run.protocol_template.default_program_id,
            points=points,
            event_type=event_type,
            event_reference_id=run.id,
            description=description,
        )
    )


def advance_protocol_phase(db: Session, run: ProtocolRun) -> bool:
    """Advance phase based on simple criteria. Returns True if moved."""
    phases = (
        db.query(ProtocolPhase)
        .filter(ProtocolPhase.protocol_template_id == run.protocol_template_id)
        .order_by(ProtocolPhase.phase_order.asc())
        .all()
    )
    if not phases:
        return False

    if run.current_phase_id is None:
        run.current_phase_id = phases[0].id
        return True

    current_index = next((i for i, phase in enumerate(phases) if phase.id == run.current_phase_id), None)
    if current_index is None or current_index >= len(phases) - 1:
        return False

    current_phase = phases[current_index]
    next_phase = phases[current_index + 1]

    artifact_keys = {
        artifact.artifact_definition.artifact_key
        for artifact in run.artifact_instances
    }
    generated_count = len(run.generated_items)

    criteria_met = False
    if current_phase.phase_key == "triage":
        criteria_met = "q_7_functions" in artifact_keys
        if criteria_met:
            award_protocol_milestone(db, run, "triage")
    elif current_phase.phase_key == "baseline":
        criteria_met = "lab_baseline_panel" in artifact_keys
        if criteria_met:
            award_protocol_milestone(db, run, "baseline")
    elif current_phase.phase_key == "intervene":
        criteria_met = generated_count > 0
    elif current_phase.phase_key == "retest":
        retest_count = sum(1 for art in run.artifact_instances if art.artifact_definition.artifact_key == "lab_baseline_panel")
        criteria_met = retest_count >= 2
        if criteria_met:
            award_protocol_milestone(db, run, "retest")

    if not criteria_met:
        return False

    run.current_phase_id = next_phase.id
    if next_phase.phase_key == "retest":
        run.status = "retest"
    if next_phase.phase_key == phases[-1].phase_key and criteria_met and current_phase.phase_key == "retest":
        run.status = "completed"
        run.completed_at = datetime.utcnow()

    return True
