from app.models import Enrollment, Program


def test_create_and_reactivate_enrollment(client, db_session):
    program = Program(name="Lifestyle", description="Desc", is_active=True)
    db_session.add(program)
    db_session.commit()
    db_session.refresh(program)

    payload = {"user_id": 101, "program_id": program.id}
    create = client.post("/api/v1/enrollments/", json=payload)
    assert create.status_code == 201

    enrollment_id = create.json()["id"]
    cancel = client.delete(f"/api/v1/enrollments/{enrollment_id}")
    assert cancel.status_code == 204

    reactivate = client.post("/api/v1/enrollments/", json=payload)
    assert reactivate.status_code == 201
    assert reactivate.json()["is_active"] is True

    db_obj = db_session.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
    assert db_obj.is_active is True


def test_create_enrollment_requires_program(client):
    response = client.post("/api/v1/enrollments/", json={"user_id": 1, "program_id": 999})
    assert response.status_code == 404
