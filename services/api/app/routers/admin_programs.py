"""Admin router for program and habit management."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.models import Program, Habit, User, Enrollment
from app.auth import require_admin

router = APIRouter(prefix="/api/v1/admin/programs", tags=["admin", "programs"])


class HabitCreate(BaseModel):
    """Schema for creating a habit within a program."""
    name: str
    description: Optional[str] = None
    points_per_completion: int = 10
    is_active: bool = True


class HabitResponse(BaseModel):
    """Schema for habit response."""
    id: int
    program_id: int
    name: str
    description: Optional[str]
    points_per_completion: int
    is_active: bool

    class Config:
        from_attributes = True


class ProgramCreate(BaseModel):
    """Schema for creating a program with habits."""
    name: str
    description: Optional[str] = None
    is_active: bool = True
    habits: List[HabitCreate] = []


class ProgramUpdate(BaseModel):
    """Schema for updating a program."""
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    habits: Optional[List[HabitCreate]] = None


class ProgramResponse(BaseModel):
    """Schema for program response with habits."""
    id: int
    name: str
    description: Optional[str]
    is_active: bool
    created_at: datetime
    habits: List[HabitResponse] = []

    class Config:
        from_attributes = True


@router.get("/", response_model=List[ProgramResponse])
def list_programs(
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
):
    """List all programs with their habits (admin only)."""
    programs = db.query(Program).order_by(Program.id).all()
    return programs


@router.get("/{program_id}", response_model=ProgramResponse)
def get_program(
    program_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
):
    """Get a specific program with habits (admin only)."""
    program = db.query(Program).filter(Program.id == program_id).first()
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    return program


@router.post("/", response_model=ProgramResponse, status_code=status.HTTP_201_CREATED)
def create_program(
    program: ProgramCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
):
    """Create a new program with habits (admin only)."""
    # Create program
    db_program = Program(
        name=program.name,
        description=program.description,
        is_active=program.is_active,
    )
    db.add(db_program)
    db.flush()  # Get program ID before adding habits

    # Create habits
    for habit_data in program.habits:
        db_habit = Habit(
            program_id=db_program.id,
            name=habit_data.name,
            description=habit_data.description,
            points_per_completion=habit_data.points_per_completion,
            is_active=habit_data.is_active,
        )
        db.add(db_habit)

    db.commit()
    db.refresh(db_program)
    return db_program


@router.put("/{program_id}", response_model=ProgramResponse)
def update_program(
    program_id: int,
    program_update: ProgramUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
):
    """Update a program and its habits (admin only)."""
    db_program = db.query(Program).filter(Program.id == program_id).first()
    if not db_program:
        raise HTTPException(status_code=404, detail="Program not found")

    # Update program fields
    if program_update.name is not None:
        db_program.name = program_update.name
    if program_update.description is not None:
        db_program.description = program_update.description
    if program_update.is_active is not None:
        db_program.is_active = program_update.is_active

    # Update habits if provided
    if program_update.habits is not None:
        # Delete all existing habits for this program
        db.query(Habit).filter(Habit.program_id == program_id).delete()

        # Create new habits
        for habit_data in program_update.habits:
            db_habit = Habit(
                program_id=program_id,
                name=habit_data.name,
                description=habit_data.description,
                points_per_completion=habit_data.points_per_completion,
                is_active=habit_data.is_active,
            )
            db.add(db_habit)

    db.commit()
    db.refresh(db_program)
    return db_program


@router.delete("/{program_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_program(
    program_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
):
    """Delete a program and cascade delete habits (admin only)."""
    db_program = db.query(Program).filter(Program.id == program_id).first()
    if not db_program:
        raise HTTPException(status_code=404, detail="Program not found")

    # Check if program has active enrollments
    active_enrollments = (
        db.query(Enrollment)
        .filter(Enrollment.program_id == program_id, Enrollment.is_active == True)
        .count()
    )

    if active_enrollments > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete program: {active_enrollments} user(s) are currently enrolled",
        )

    # Delete program (habits will cascade delete due to relationship)
    db.delete(db_program)
    db.commit()
    return None


@router.post("/{program_id}/habits", response_model=HabitResponse, status_code=status.HTTP_201_CREATED)
def add_habit_to_program(
    program_id: int,
    habit: HabitCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
):
    """Add a single habit to an existing program (admin only)."""
    # Verify program exists
    program = db.query(Program).filter(Program.id == program_id).first()
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")

    db_habit = Habit(
        program_id=program_id,
        name=habit.name,
        description=habit.description,
        points_per_completion=habit.points_per_completion,
        is_active=habit.is_active,
    )
    db.add(db_habit)
    db.commit()
    db.refresh(db_habit)
    return db_habit


@router.delete("/{program_id}/habits/{habit_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_habit_from_program(
    program_id: int,
    habit_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
):
    """Remove a habit from a program (admin only)."""
    habit = (
        db.query(Habit)
        .filter(Habit.id == habit_id, Habit.program_id == program_id)
        .first()
    )

    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found in this program")

    db.delete(habit)
    db.commit()
    return None
