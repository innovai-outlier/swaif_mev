"""Protocol run progress tracking and reminder logic."""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models import ProtocolRun, Reminder, Habit

def track_protocol_progress_and_schedule_reminders(db: Session, protocol_run_id: int):
    """Track progress and schedule reminders for a protocol run."""
    run = db.query(ProtocolRun).filter_by(id=protocol_run_id).first()
    if not run:
        return None
    # Example: schedule reminders for all habits in the run for the next 7 days
    habits = db.query(Habit).filter_by(program_id=run.program_id).all()
    reminders = []
    for habit in habits:
        for day in range(7):
            scheduled_for = datetime.utcnow() + timedelta(days=day)
            reminder = Reminder(
                user_id=run.user_id,
                habit_id=habit.id,
                scheduled_for=scheduled_for,
                status="pending",
                message=f"Don't forget to complete your habit: {habit.name}"
            )
            db.add(reminder)
            reminders.append(reminder)
    db.commit()
    return reminders
