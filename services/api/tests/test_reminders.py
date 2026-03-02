from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db, TestingSessionLocal
from app.models import Reminder, User, Habit
from datetime import datetime, timedelta
import pytest

client = TestClient(app)

def setup_module():
    db = TestingSessionLocal()
    from app.database import Base, engine
    Base.metadata.create_all(bind=engine)
    db.query(Reminder).delete()
    db.query(Habit).filter(Habit.name == "Test Habit").delete()
    db.query(User).filter(User.email == "test@example.com").delete()
    db.commit()
    db.add(User(email="test@example.com", full_name="Test User", hashed_password="x", role="patient"))
    db.add(Habit(name="Test Habit", description="Test", program_id=1, points_per_completion=5))
    db.commit()
    db.close()

def test_create_and_list_reminders():
    scheduled_for = (datetime.utcnow() + timedelta(hours=1)).isoformat()
    resp = client.post("/api/v1/reminders/", json={
        "user_id": 1,
        "habit_id": 1,
        "scheduled_for": scheduled_for,
        "message": "Test reminder"
    })
    assert resp.status_code == 201
    reminder_id = resp.json()["id"]

    list_resp = client.get(f"/api/v1/reminders?user_id=1")
    assert list_resp.status_code == 200
    reminders = list_resp.json()
    assert any(r["id"] == reminder_id for r in reminders)

def test_update_reminder_status():
    scheduled_for = (datetime.utcnow() + timedelta(hours=2)).isoformat()
    resp = client.post("/api/v1/reminders/", json={
        "user_id": 1,
        "habit_id": 1,
        "scheduled_for": scheduled_for,
        "message": "Update status"
    })
    reminder_id = resp.json()["id"]
    patch_resp = client.patch(f"/api/v1/reminders/{reminder_id}", json={"status": "sent"})
    assert patch_resp.status_code == 200
    assert patch_resp.json()["status"] == "sent"
