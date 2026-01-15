"""Habits API endpoints."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Habit, Program
from app.schemas import HabitCreate, HabitUpdate, HabitResponse

router = APIRouter(prefix="/api/v1/habits", tags=["habits"])


@router.get("/", response_model=List[HabitResponse])
def list_habits(
    skip: int = 0,
    limit: int = 100,
    program_id: int = None,
    is_active: bool = None,
    db: Session = Depends(get_db),
):
    """List all habits with optional filtering."""
    query = db.query(Habit)
    if program_id is not None:
        query = query.filter(Habit.program_id == program_id)
    if is_active is not None:
        query = query.filter(Habit.is_active == is_active)
    habits = query.offset(skip).limit(limit).all()
    return habits


@router.get("/{habit_id}", response_model=HabitResponse)
def get_habit(habit_id: int, db: Session = Depends(get_db)):
    """Get a specific habit by ID."""
    habit = db.query(Habit).filter(Habit.id == habit_id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    return habit


@router.post("/", response_model=HabitResponse, status_code=status.HTTP_201_CREATED)
def create_habit(habit: HabitCreate, db: Session = Depends(get_db)):
    """Create a new habit."""
    # Verify program exists
    program = db.query(Program).filter(Program.id == habit.program_id).first()
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")

    db_habit = Habit(**habit.model_dump())
    db.add(db_habit)
    db.commit()
    db.refresh(db_habit)
    return db_habit


@router.patch("/{habit_id}", response_model=HabitResponse)
def update_habit(
    habit_id: int, habit_update: HabitUpdate, db: Session = Depends(get_db)
):
    """Update a habit."""
    db_habit = db.query(Habit).filter(Habit.id == habit_id).first()
    if not db_habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    update_data = habit_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_habit, key, value)

    db.commit()
    db.refresh(db_habit)
    return db_habit


@router.delete("/{habit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_habit(habit_id: int, db: Session = Depends(get_db)):
    """Delete a habit (soft delete by setting is_active=False)."""
    db_habit = db.query(Habit).filter(Habit.id == habit_id).first()
    if not db_habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    db_habit.is_active = False
    db.commit()
    return None
