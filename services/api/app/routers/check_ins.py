"""Check-ins API endpoints."""
from typing import List
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models import CheckIn, Habit, PointsLedger, Streak
from app.schemas import CheckInCreate, CheckInResponse

router = APIRouter(prefix="/api/v1/check-ins", tags=["check-ins"])


@router.get("/", response_model=List[CheckInResponse])
def list_check_ins(
    user_id: int = None,
    habit_id: int = None,
    start_date: date = None,
    end_date: date = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """List check-ins with optional filtering."""
    query = db.query(CheckIn)
    if user_id is not None:
        query = query.filter(CheckIn.user_id == user_id)
    if habit_id is not None:
        query = query.filter(CheckIn.habit_id == habit_id)
    if start_date is not None:
        query = query.filter(CheckIn.check_in_date >= start_date)
    if end_date is not None:
        query = query.filter(CheckIn.check_in_date <= end_date)

    check_ins = query.order_by(CheckIn.check_in_date.desc()).offset(skip).limit(limit).all()
    return check_ins


@router.get("/{check_in_id}", response_model=CheckInResponse)
def get_check_in(check_in_id: int, db: Session = Depends(get_db)):
    """Get a specific check-in by ID."""
    check_in = db.query(CheckIn).filter(CheckIn.id == check_in_id).first()
    if not check_in:
        raise HTTPException(status_code=404, detail="Check-in not found")
    return check_in


@router.post("/", response_model=CheckInResponse, status_code=status.HTTP_201_CREATED)
def create_check_in(check_in: CheckInCreate, db: Session = Depends(get_db)):
    """Create a new check-in and award points."""
    # Verify habit exists
    habit = db.query(Habit).filter(Habit.id == check_in.habit_id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    # Create check-in
    db_check_in = CheckIn(**check_in.model_dump())

    try:
        db.add(db_check_in)
        db.flush()  # Get the ID but don't commit yet

        # Award points to ledger
        points_entry = PointsLedger(
            user_id=check_in.user_id,
            program_id=habit.program_id,
            points=habit.points_per_completion,
            event_type="check_in",
            event_reference_id=db_check_in.id,
            description=f"Check-in: {habit.name}",
        )
        db.add(points_entry)

        # Update or create streak
        streak = (
            db.query(Streak)
            .filter(
                Streak.user_id == check_in.user_id,
                Streak.habit_id == check_in.habit_id,
            )
            .first()
        )

        if streak:
            # Check if consecutive day
            if streak.last_check_in_date:
                days_diff = (check_in.check_in_date - streak.last_check_in_date).days
                if days_diff == 1:
                    streak.current_streak += 1
                    if streak.current_streak > streak.longest_streak:
                        streak.longest_streak = streak.current_streak
                elif days_diff > 1:
                    streak.current_streak = 1
            else:
                streak.current_streak = 1
            streak.last_check_in_date = check_in.check_in_date
        else:
            # Create new streak
            streak = Streak(
                user_id=check_in.user_id,
                habit_id=check_in.habit_id,
                program_id=habit.program_id,
                current_streak=1,
                longest_streak=1,
                last_check_in_date=check_in.check_in_date,
            )
            db.add(streak)

        db.commit()
        db.refresh(db_check_in)
        return db_check_in

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Check-in already exists for this habit on this date",
        )
