"""Enrollments API endpoints."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models import Enrollment, Program
from app.schemas import EnrollmentCreate, EnrollmentResponse

router = APIRouter(prefix="/api/v1/enrollments", tags=["enrollments"])


@router.get("/", response_model=List[EnrollmentResponse])
def list_enrollments(
    user_id: int = None,
    program_id: int = None,
    is_active: bool = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """List enrollments with optional filtering."""
    query = db.query(Enrollment)
    
    if user_id is not None:
        query = query.filter(Enrollment.user_id == user_id)
    if program_id is not None:
        query = query.filter(Enrollment.program_id == program_id)
    if is_active is not None:
        query = query.filter(Enrollment.is_active == is_active)
    
    enrollments = query.offset(skip).limit(limit).all()
    return enrollments


@router.post("/", response_model=EnrollmentResponse, status_code=status.HTTP_201_CREATED)
def create_enrollment(enrollment: EnrollmentCreate, db: Session = Depends(get_db)):
    """Enroll a user in a program."""
    # Verify program exists
    program = db.query(Program).filter(Program.id == enrollment.program_id).first()
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Program {enrollment.program_id} not found",
        )
    
    # Check for existing enrollment
    existing = db.query(Enrollment).filter(
        Enrollment.user_id == enrollment.user_id,
        Enrollment.program_id == enrollment.program_id
    ).first()
    
    if existing:
        if existing.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already enrolled in this program",
            )
        else:
            # Reactivate existing enrollment
            existing.is_active = True
            db.commit()
            db.refresh(existing)
            return existing
    
    # Create new enrollment
    try:
        db_enrollment = Enrollment(**enrollment.model_dump())
        db.add(db_enrollment)
        db.commit()
        db.refresh(db_enrollment)
        return db_enrollment
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Enrollment creation failed",
        )


@router.delete("/{enrollment_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_enrollment(enrollment_id: int, db: Session = Depends(get_db)):
    """Cancel/deactivate an enrollment (soft delete)."""
    enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Enrollment {enrollment_id} not found",
        )
    
    enrollment.is_active = False
    db.commit()
    return None
