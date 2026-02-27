"""Admin endpoints for protocol templates."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import require_admin
from app.database import get_db
from app.models import ProtocolTemplate
from app.schemas import ProtocolTemplateCreate, ProtocolTemplateOut, ProtocolTemplateUpdate

router = APIRouter(prefix="/api/v1/admin/protocol-templates", tags=["admin-protocol-templates"])


@router.get("/", response_model=List[ProtocolTemplateOut])
def list_protocol_templates(db: Session = Depends(get_db), _=Depends(require_admin)):
    return db.query(ProtocolTemplate).order_by(ProtocolTemplate.id.desc()).all()


@router.post("/", response_model=ProtocolTemplateOut, status_code=status.HTTP_201_CREATED)
def create_protocol_template(
    payload: ProtocolTemplateCreate,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    exists = db.query(ProtocolTemplate).filter(ProtocolTemplate.code == payload.code).first()
    if exists:
        raise HTTPException(status_code=400, detail="Template code already exists")

    template = ProtocolTemplate(**payload.model_dump())
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


@router.get("/{template_id}", response_model=ProtocolTemplateOut)
def get_protocol_template(template_id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    template = db.query(ProtocolTemplate).filter(ProtocolTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Protocol template not found")
    return template


@router.put("/{template_id}", response_model=ProtocolTemplateOut)
def update_protocol_template(
    template_id: int,
    payload: ProtocolTemplateUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    template = db.query(ProtocolTemplate).filter(ProtocolTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Protocol template not found")

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(template, key, value)

    db.commit()
    db.refresh(template)
    return template
