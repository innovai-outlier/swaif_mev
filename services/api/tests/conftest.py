from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.auth import get_password_hash
from app.database import get_db
from app.main import app
from app.models import Base, User


@pytest.fixture()
def db_session(tmp_path: Path):
    db_path = tmp_path / "test.db"
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def admin_user(db_session):
    user = User(
        email="admin@example.com",
        full_name="Admin User",
        hashed_password=get_password_hash("adminpass123"),
        role="admin",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture()
def patient_user(db_session):
    user = User(
        email="patient@example.com",
        full_name="Patient User",
        hashed_password=get_password_hash("patientpass123"),
        role="patient",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture()
def admin_token(client, admin_user):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": admin_user.email, "password": "adminpass123"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture()
def auth_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}
