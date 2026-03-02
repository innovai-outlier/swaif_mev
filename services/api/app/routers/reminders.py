"""Reminders API endpoints."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Reminder
from app.schemas import ReminderCreate, ReminderResponse


router = APIRouter(prefix="/api/v1/reminders", tags=["reminders"])

@router.get("/", response_model=List[ReminderResponse])
def list_reminders(user_id: int = None, habit_id: int = None, db: Session = Depends(get_db)):
    """List reminders with optional filtering."""
    query = db.query(Reminder)
    if user_id is not None:
        query = query.filter(Reminder.user_id == user_id)
    if habit_id is not None:
        query = query.filter(Reminder.habit_id == habit_id)
    reminders = query.order_by(Reminder.scheduled_for.asc()).all()
    return reminders

@router.get("/{reminder_id}", response_model=ReminderResponse)
def get_reminder(reminder_id: int, db: Session = Depends(get_db)):
    reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return reminder


@router.post("/", response_model=ReminderResponse, status_code=status.HTTP_201_CREATED)
def create_reminder(reminder: ReminderCreate, db: Session = Depends(get_db)):
    db_reminder = Reminder(**reminder.model_dump())
    db.add(db_reminder)
    db.commit()
    db.refresh(db_reminder)
    return db_reminder

# PATCH endpoint for updating reminders
from fastapi import Body

@router.patch("/{reminder_id}", response_model=ReminderResponse)
def update_reminder(reminder_id: int, status: str = Body(None), sent_at: str = Body(None), db: Session = Depends(get_db)):
    reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    if status:
        reminder.status = status
    if sent_at:
        from datetime import datetime
        reminder.sent_at = datetime.fromisoformat(sent_at)
    db.commit()
    db.refresh(reminder)
    return reminder
