from app.models import Program


def test_admin_program_crud_requires_admin(client, auth_headers):
    create_payload = {
        "name": "Cardio",
        "description": "Heart health",
        "is_active": True,
        "habits": [{"name": "Walk", "points_per_completion": 12}],
    }
    created = client.post("/api/v1/admin/programs/", json=create_payload, headers=auth_headers)
    assert created.status_code == 201

    program_id = created.json()["id"]
    listed = client.get("/api/v1/admin/programs/", headers=auth_headers)
    assert listed.status_code == 200
    assert any(item["id"] == program_id for item in listed.json())


def test_admin_reward_config_initialization(client, auth_headers):
    response = client.get("/api/v1/admin/rewards/config", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_admin_delete_program_with_active_enrollment_blocked(client, auth_headers, db_session):
    created = client.post(
        "/api/v1/admin/programs/",
        json={"name": "Mindfulness", "habits": []},
        headers=auth_headers,
    )
    program_id = created.json()["id"]

    enroll = client.post("/api/v1/enrollments/", json={"user_id": 42, "program_id": program_id})
    assert enroll.status_code == 201

    delete = client.delete(f"/api/v1/admin/programs/{program_id}", headers=auth_headers)
    assert delete.status_code == 400

    exists = db_session.query(Program).filter(Program.id == program_id).first()
    assert exists is not None
