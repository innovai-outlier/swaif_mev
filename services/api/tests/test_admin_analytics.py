from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.auth import get_current_user, require_admin
from app.database import Base, get_db
from app.main import app
from app.models import User, Program, Enrollment, CheckIn, PointsLedger, Badge, UserBadge
from app.seed_young_forever import seed_young_forever_core

en = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=en)

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
    Base.metadata.create_all(bind=en)

def teardown_module():
    Base.metadata.drop_all(bind=en)

def test_admin_analytics_endpoints():
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[require_admin] = override_admin
    app.dependency_overrides[get_current_user] = override_current_user

    db = TestingSessionLocal()
    db.add(User(email="admin@example.com", full_name="Admin", hashed_password="x", role="admin"))
    db.add(User(email="p3@example.com", full_name="Paciente 3", hashed_password="x", role="patient"))
    db.add(Program(name="Base", description="Base"))
    db.commit()
    seed_young_forever_core(db)
    db.close()

    client = TestClient(app)

    # Create protocol run and generate habit
    create_run = client.post(
        "/api/v1/protocol-runs/",
        json={"user_id": 2, "template_code": "young_forever_core_v1"},
    )
    assert create_run.status_code == 201
    run_id = create_run.json()["id"]
    gen_resp = client.post(f"/api/v1/protocol-runs/{run_id}/generate-interventions")
    assert gen_resp.status_code == 200
    generated_habit_id = gen_resp.json()["generated_habit_ids"][0]

    # Perform check-in to generate analytics data
    checkin_resp = client.post(
        "/api/v1/check-ins/",
        json={
            "user_id": 2,
            "habit_id": generated_habit_id,
            "check_in_date": "2026-02-28",
            "metric_key": "sleep_hours",
            "value_numeric": 7.5,
        },
    )
    assert checkin_resp.status_code == 201

    # Award badge
    badge_resp = client.post(
        "/api/v1/badges/",
        json={"name": "Consistent", "description": "Consistent habit", "points_reward": 5},
    )
    assert badge_resp.status_code == 201
    badge_id = badge_resp.json()["id"]
    award_resp = client.post(
        "/api/v1/badges/award",
        json={"user_id": 2, "badge_id": badge_id},
    )
    assert award_resp.status_code == 201

    # Test analytics overview endpoint
    overview = client.get("/api/v1/admin/analytics/overview")
    assert overview.status_code == 200
    data = overview.json()
    assert "overview" in data and data["overview"]["total_patients"] >= 1
    assert data["overview"]["total_checkins"] >= 1
    assert data["overview"]["total_badges_awarded"] >= 1

    # Test engagement trends endpoint
    trends = client.get("/api/v1/admin/analytics/engagement-trends?days=7")
    assert trends.status_code == 200
    trends_data = trends.json()
    assert "daily_checkins" in trends_data
    assert "daily_active_users" in trends_data

    # Test program performance endpoint
    perf = client.get("/api/v1/admin/analytics/program-performance")
    assert perf.status_code == 200
    perf_data = perf.json()
    assert "programs" in perf_data
    assert any(p["enrollment_count"] >= 0 for p in perf_data["programs"])

    # Test badge statistics endpoint
    badge_stats = client.get("/api/v1/admin/analytics/badge-statistics")
    assert badge_stats.status_code == 200
    badge_stats_data = badge_stats.json()
    assert "badge_details" in badge_stats_data
    assert any(b["times_awarded"] >= 1 for b in badge_stats_data["badge_details"])

    app.dependency_overrides.clear()
