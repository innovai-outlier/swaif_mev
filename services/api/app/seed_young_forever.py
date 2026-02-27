"""Seed for young_forever_core_v1 protocol template and related assets."""
from app.database import SessionLocal
from app.models import (
    ArtifactDefinition,
    InterventionTemplate,
    Program,
    ProtocolPhase,
    ProtocolTemplate,
)


def seed_young_forever_core(db):
    template = db.query(ProtocolTemplate).filter(ProtocolTemplate.code == "young_forever_core_v1").first()
    if template:
        return template

    program = db.query(Program).filter(Program.name == "Young Forever - Core").first()
    if not program:
        program = Program(
            name="Young Forever - Core",
            description="Programa base para hábitos gerados pelo protocolo Young Forever",
            is_active=True,
        )
        db.add(program)
        db.flush()

    template = ProtocolTemplate(
        code="young_forever_core_v1",
        name="Young Forever Core",
        version="v1",
        description="Jornada clínica baseada em Jovem Para Sempre - Parte III",
        is_active=True,
        default_program_id=program.id,
    )
    db.add(template)
    db.flush()

    phases = [
        ("Triagem", "triage", 1),
        ("Baseline", "baseline", 2),
        ("Intervenção", "intervene", 3),
        ("Reteste", "retest", 4),
    ]
    for name, key, order in phases:
        db.add(
            ProtocolPhase(
                protocol_template_id=template.id,
                name=name,
                phase_key=key,
                phase_order=order,
            )
        )

    db.add_all(
        [
            ArtifactDefinition(
                protocol_template_id=template.id,
                artifact_key="q_7_functions",
                type="questionnaire",
                name="Questionário 7 Funções",
                schema_json={"responses": "dict[str, number|bool]"},
                scoring_json={"strategy": "max_score_priority"},
            ),
            ArtifactDefinition(
                protocol_template_id=template.id,
                artifact_key="lab_baseline_panel",
                type="lab_panel",
                name="Painel Laboratorial Baseline",
                schema_json={"markers": ["glicose", "insulina", "PCR", "TSH"]},
            ),
            ArtifactDefinition(
                protocol_template_id=template.id,
                artifact_key="wearable_core",
                type="wearable",
                name="Wearable Core",
                schema_json={"metrics": ["sleep_hours", "resting_hr", "steps"]},
            ),
        ]
    )

    db.add_all(
        [
            InterventionTemplate(
                protocol_template_id=template.id,
                intervention_key="sleep_foundation",
                type="habit",
                name="Sono Fundação",
                description="Dormir e acordar em horário consistente",
                habit_blueprint_json={"points_per_completion": 15, "target_metric_key": "sleep_hours"},
                activation_rules_json={"top_function": "sleep"},
            ),
            InterventionTemplate(
                protocol_template_id=template.id,
                intervention_key="movement_base",
                type="habit",
                name="Movimento Diário",
                description="Atingir meta mínima de movimento diário",
                habit_blueprint_json={"points_per_completion": 12, "target_metric_key": "steps"},
                activation_rules_json={},
            ),
            InterventionTemplate(
                protocol_template_id=template.id,
                intervention_key="nutrition_base",
                type="habit",
                name="Alimentação Base",
                description="Prato base com proteína + vegetais + fibras",
                habit_blueprint_json={"points_per_completion": 12, "target_metric_key": "energy_0_10"},
                activation_rules_json={},
            ),
        ]
    )

    db.commit()
    db.refresh(template)
    return template


def main():
    db = SessionLocal()
    try:
        seed_young_forever_core(db)
        print("Seed young_forever_core_v1 concluído.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
