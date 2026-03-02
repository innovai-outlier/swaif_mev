from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth import get_current_user, require_admin
from app.database import Base, get_db
from app.main import app
from app.models import User, Program, Badge, PointsLedger, Streak, UserBadge, Habit
from app.seed_young_forever import seed_young_forever_core

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class DummyUser:
    id = 999
    role = "admin"

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def override_admin():
    return DummyUser()

def override_current_user():
    return DummyUser()

def setup_module():
    Base.metadata.create_all(bind=engine)

def teardown_module():
    Base.metadata.drop_all(bind=engine)

def test_pointsledger_streak_badge_flow():
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[require_admin] = override_admin
    app.dependency_overrides[get_current_user] = override_current_user

    db = TestingSessionLocal()
    db.add(User(email="p2@example.com", full_name="Paciente 2", hashed_password="x", role="patient"))
    db.add(Program(name="Base", description="Base"))
    db.commit()
    seed_young_forever_core(db)
    db.close()

    client = TestClient(app)

    # Create protocol run and generate habit
    create_run = client.post(
        "/api/v1/protocol-runs/",
        json={"user_id": 1, "template_code": "young_forever_core_v1"},
    )
    assert create_run.status_code == 201
    run_id = create_run.json()["id"]

    gen_resp = client.post(f"/api/v1/protocol-runs/{run_id}/generate-interventions")
    assert gen_resp.status_code == 200
    generated_habit_id = gen_resp.json()["generated_habit_ids"][0]

    # Perform check-in to trigger points and streak
    checkin_resp = client.post(
        "/api/v1/check-ins/",
        json={
            "user_id": 1,
            "habit_id": generated_habit_id,
            "check_in_date": date.today().isoformat(),
            "metric_key": "sleep_hours",
            "value_numeric": 7.5,
        },
    )
    assert checkin_resp.status_code == 201
    # Check PointsLedger entry
    db = TestingSessionLocal()
    points_entries = db.query(PointsLedger).filter_by(user_id=1).all()
    assert any(e.event_type == "check_in" for e in points_entries)
    # Check Streak entry
    streak = db.query(Streak).filter_by(user_id=1, habit_id=generated_habit_id).first()
    assert streak is not None and streak.current_streak >= 1
    db.close()

    # Award badge and check points
    badge_resp = client.post(
        "/api/v1/badges/",
        json={"name": "Early Bird", "description": "Wake up early", "points_reward": 10},
    )
    assert badge_resp.status_code == 201
    badge_id = badge_resp.json()["id"]
    award_resp = client.post(
        "/api/v1/badges/award",
        json={"user_id": 1, "badge_id": badge_id},
    )
    assert award_resp.status_code == 201
    db = TestingSessionLocal()
    badge_points = db.query(PointsLedger).filter_by(user_id=1, event_type="badge_earned").first()
    assert badge_points is not None and badge_points.points == 10
    user_badge = db.query(UserBadge).filter_by(user_id=1, badge_id=badge_id).first()
    assert user_badge is not None
    db.close()

    app.dependency_overrides.clear()
