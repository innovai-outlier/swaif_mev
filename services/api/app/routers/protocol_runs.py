"""Endpoints for protocol run lifecycle and artifact submissions."""
from datetime import datetime
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.auth import get_current_user, require_admin
from app.database import get_db
from app.models import (
    ArtifactDefinition,
    ArtifactInstance,
    ProtocolPhase,
    ProtocolRun,
    ProtocolTemplate,
)
from app.protocol_engine import (
    advance_protocol_phase,
    compute_artifact_scores,
    generate_habits_from_interventions,
)
from app.schemas import (
    ArtifactInstanceCreate,
    ArtifactInstanceOut,
    GenerateInterventionsResponse,
    PhaseAdvanceResponse,
    ProtocolRunCreate,
    ProtocolRunOut,
)

router = APIRouter(prefix="/api/v1/protocol-runs", tags=["protocol-runs"])


@router.post("/", response_model=ProtocolRunOut, status_code=status.HTTP_201_CREATED)
def create_protocol_run(
    payload: ProtocolRunCreate,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    template = (
        db.query(ProtocolTemplate)
        .filter(ProtocolTemplate.code == payload.template_code, ProtocolTemplate.is_active.is_(True))
        .first()
    )
    if not template:
        raise HTTPException(status_code=404, detail="Protocol template not found")

    first_phase = (
        db.query(ProtocolPhase)
        .filter(ProtocolPhase.protocol_template_id == template.id)
        .order_by(ProtocolPhase.phase_order.asc())
        .first()
    )

    run = ProtocolRun(
        user_id=payload.user_id,
        protocol_template_id=template.id,
        status="active",
        current_phase_id=first_phase.id if first_phase else None,
        started_at=datetime.utcnow(),
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


@router.get("/{run_id}", response_model=ProtocolRunOut)
def get_protocol_run(
    run_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    run = db.query(ProtocolRun).filter(ProtocolRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Protocol run not found")
    return run


@router.post("/{run_id}/artifacts/{artifact_key}", response_model=ArtifactInstanceOut)
def submit_artifact(
    run_id: int,
    artifact_key: str,
    payload: ArtifactInstanceCreate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    run = (
        db.query(ProtocolRun)
        .options(joinedload(ProtocolRun.protocol_template))
        .filter(ProtocolRun.id == run_id)
        .first()
    )
    if not run:
        raise HTTPException(status_code=404, detail="Protocol run not found")

    definition = (
        db.query(ArtifactDefinition)
        .filter(
            ArtifactDefinition.protocol_template_id == run.protocol_template_id,
            ArtifactDefinition.artifact_key == artifact_key,
        )
        .first()
    )
    if not definition:
        raise HTTPException(status_code=404, detail="Artifact definition not found")

    computed = compute_artifact_scores(artifact_key=artifact_key, payload=payload.payload_json)
    instance = ArtifactInstance(
        protocol_run_id=run.id,
        artifact_definition_id=definition.id,
        payload_json=payload.payload_json,
        computed_json=computed,
        source=payload.source,
        collected_at=datetime.utcnow(),
    )
    db.add(instance)
    db.commit()
    db.refresh(instance)
    return instance


@router.post("/{run_id}/generate-interventions", response_model=GenerateInterventionsResponse)
def generate_interventions(
    run_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    run = (
        db.query(ProtocolRun)
        .options(joinedload(ProtocolRun.protocol_template))
        .filter(ProtocolRun.id == run_id)
        .first()
    )
    if not run:
        raise HTTPException(status_code=404, detail="Protocol run not found")

    generated_habit_ids = generate_habits_from_interventions(db, run)
    db.commit()
    return GenerateInterventionsResponse(
        generated_habit_ids=generated_habit_ids,
        generated_count=len(generated_habit_ids),
    )


@router.post("/{run_id}/advance-phase", response_model=PhaseAdvanceResponse)
def advance_phase(
    run_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    run = (
        db.query(ProtocolRun)
        .options(
            joinedload(ProtocolRun.artifact_instances).joinedload(ArtifactInstance.artifact_definition),
            joinedload(ProtocolRun.generated_items),
            joinedload(ProtocolRun.protocol_template),
            joinedload(ProtocolRun.current_phase),
        )
        .filter(ProtocolRun.id == run_id)
        .first()
    )
    if not run:
        raise HTTPException(status_code=404, detail="Protocol run not found")

    advanced = advance_protocol_phase(db, run)
    db.commit()
    db.refresh(run)
    phase_name = run.current_phase.phase_key if run.current_phase else None
    return PhaseAdvanceResponse(advanced=advanced, current_phase=phase_name)


@router.get("/{run_id}/timeline")
def run_timeline(
    run_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
) -> Dict:
    run = (
        db.query(ProtocolRun)
        .options(
            joinedload(ProtocolRun.protocol_template).joinedload(ProtocolTemplate.phases),
            joinedload(ProtocolRun.artifact_instances).joinedload(ArtifactInstance.artifact_definition),
            joinedload(ProtocolRun.generated_items),
        )
        .filter(ProtocolRun.id == run_id)
        .first()
    )
    if not run:
        raise HTTPException(status_code=404, detail="Protocol run not found")

    return {
        "run_id": run.id,
        "status": run.status,
        "current_phase_id": run.current_phase_id,
        "phases": [
            {"id": phase.id, "phase_key": phase.phase_key, "phase_order": phase.phase_order}
            for phase in sorted(run.protocol_template.phases, key=lambda p: p.phase_order)
        ],
        "artifacts": [
            {
                "artifact_key": item.artifact_definition.artifact_key,
                "collected_at": item.collected_at,
                "computed_json": item.computed_json,
            }
            for item in sorted(run.artifact_instances, key=lambda a: a.collected_at)
        ],
        "generated_interventions": [
            {
                "id": item.id,
                "intervention_template_id": item.intervention_template_id,
                "generated_habit_id": item.generated_habit_id,
            }
            for item in run.generated_items
        ],
    }
