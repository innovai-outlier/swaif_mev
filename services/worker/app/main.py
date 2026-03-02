"""Worker entrypoint with Celery tasks for protocol recomputation."""
import os
from celery import Celery


REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

celery_app = Celery("mev_worker", broker=REDIS_URL, backend=REDIS_URL)



# Reminder scheduling logic
from datetime import datetime, timedelta
import requests

API_URL = os.getenv("API_URL", "http://api:8000/api/v1/reminders")

@celery_app.task(name="schedule_reminder")
def schedule_reminder(user_id: int, habit_id: int, scheduled_for: str, message: str = None):
    """Schedule a reminder for a habit check-in."""
    payload = {
        "user_id": user_id,
        "habit_id": habit_id,
        "scheduled_for": scheduled_for,
        "message": message,
    }
    resp = requests.post(API_URL, json=payload)
    return resp.json()

@celery_app.task(name="send_due_reminders")
def send_due_reminders():
    """Send reminders that are due (scheduled_for <= now, status=pending)."""
    now = datetime.utcnow().isoformat()
    resp = requests.get(f"{API_URL}?status=pending")
    reminders = resp.json()
    sent = []
    for reminder in reminders:
        if reminder["scheduled_for"] <= now:
            # Simulate sending (e.g., email, push)
            # Mark as sent
            update = requests.patch(f"{API_URL}/{reminder['id']}", json={"sent_at": now, "status": "sent"})
            sent.append(reminder["id"])
    return {"sent": sent}

@celery_app.task(name="update_reminder_status")
def update_reminder_status(reminder_id: int, status: str):
    """Update the status of a reminder."""
    resp = requests.patch(f"{API_URL}/{reminder_id}", json={"status": status})
    return resp.json()


if __name__ == "__main__":
    celery_app.worker_main(["worker", "--loglevel=info"])
