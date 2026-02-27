from app.models import User


def test_login_and_me_flow(client, admin_user):
    login = client.post(
        "/api/v1/auth/login",
        json={"email": admin_user.email, "password": "adminpass123"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]

    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == admin_user.email


def test_admin_can_register_user(client, auth_headers, db_session):
    payload = {
        "email": "new-patient@example.com",
        "full_name": "New Patient",
        "password": "secure123",
        "role": "patient",
    }

    response = client.post("/api/v1/auth/register", json=payload, headers=auth_headers)
    assert response.status_code == 201
    assert response.json()["role"] == "patient"

    created = db_session.query(User).filter(User.email == payload["email"]).first()
    assert created is not None


def test_non_admin_cannot_list_users(client, patient_user):
    login = client.post(
        "/api/v1/auth/login",
        json={"email": patient_user.email, "password": "patientpass123"},
    )
    token = login.json()["access_token"]

    response = client.get("/api/v1/auth/users", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
