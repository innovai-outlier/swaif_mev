"""Programs API endpoints."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Program, Habit
from app.schemas import ProgramCreate, ProgramUpdate, ProgramResponse, HabitResponse

router = APIRouter(prefix="/api/v1/programs", tags=["programs"])


@router.get("/", response_model=List[ProgramResponse])
def list_programs(
    skip: int = 0,
    limit: int = 100,
    is_active: bool = None,
    db: Session = Depends(get_db),
):
    """List all programs with optional filtering."""
    query = db.query(Program)
    if is_active is not None:
        query = query.filter(Program.is_active == is_active)
    programs = query.offset(skip).limit(limit).all()
    return programs


@router.get("/{program_id}", response_model=ProgramResponse)
def get_program(program_id: int, db: Session = Depends(get_db)):
    """Get a specific program by ID."""
    program = db.query(Program).filter(Program.id == program_id).first()
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    return program


@router.post("/", response_model=ProgramResponse, status_code=status.HTTP_201_CREATED)
def create_program(program: ProgramCreate, db: Session = Depends(get_db)):
    """Create a new program."""
    db_program = Program(**program.model_dump())
    db.add(db_program)
    db.commit()
    db.refresh(db_program)
    return db_program


@router.patch("/{program_id}", response_model=ProgramResponse)
def update_program(
    program_id: int, program_update: ProgramUpdate, db: Session = Depends(get_db)
):
    """Update a program."""
    db_program = db.query(Program).filter(Program.id == program_id).first()
    if not db_program:
        raise HTTPException(status_code=404, detail="Program not found")

    update_data = program_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_program, key, value)

    db.commit()
    db.refresh(db_program)
    return db_program


@router.delete("/{program_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_program(program_id: int, db: Session = Depends(get_db)):
    """Delete a program (soft delete by setting is_active=False)."""
    db_program = db.query(Program).filter(Program.id == program_id).first()
    if not db_program:
        raise HTTPException(status_code=404, detail="Program not found")

    db_program.is_active = False
    db.commit()
    return None


@router.get("/{program_id}/habits", response_model=List[HabitResponse])
def list_program_habits(program_id: int, db: Session = Depends(get_db)):
    """List all habits for a specific program."""
    program = db.query(Program).filter(Program.id == program_id).first()
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")

    habits = db.query(Habit).filter(Habit.program_id == program_id).all()
    return habits
