from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth import get_current_user, require_admin
from app.database import Base, get_db
from app.main import app
from app.models import Program, User
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


def test_protocol_end_to_end_flow():
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[require_admin] = override_admin
    app.dependency_overrides[get_current_user] = override_current_user

    db = TestingSessionLocal()
    db.add(User(email="p1@example.com", full_name="Paciente 1", hashed_password="x", role="patient"))
    db.add(Program(name="Base", description="Base"))
    db.commit()
    seed_young_forever_core(db)
    db.close()

    client = TestClient(app)

    create_run = client.post(
        "/api/v1/protocol-runs/",
        json={"user_id": 1, "template_code": "young_forever_core_v1"},
    )
    assert create_run.status_code == 201
    run_id = create_run.json()["id"]

    artifact_resp = client.post(
        f"/api/v1/protocol-runs/{run_id}/artifacts/q_7_functions",
        json={"payload_json": {"responses": {"sleep": 9, "metabolic": 5, "stress": 4}}, "source": "admin"},
    )
    assert artifact_resp.status_code == 200
    assert artifact_resp.json()["computed_json"]["top_function"] == "sleep"

    gen_resp = client.post(f"/api/v1/protocol-runs/{run_id}/generate-interventions")
    assert gen_resp.status_code == 200
    assert gen_resp.json()["generated_count"] >= 1

    habits_resp = client.get("/api/v1/habits/?source_type=protocol")
    assert habits_resp.status_code == 200

    generated_habit_id = gen_resp.json()["generated_habit_ids"][0]
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
    assert checkin_resp.json()["metric_key"] == "sleep_hours"

    advance_resp = client.post(f"/api/v1/protocol-runs/{run_id}/advance-phase")
    assert advance_resp.status_code == 200
    assert advance_resp.json()["advanced"] is True

    app.dependency_overrides.clear()
