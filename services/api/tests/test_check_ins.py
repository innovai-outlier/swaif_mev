from datetime import date

from app.models import Habit, PointsLedger, Program, Streak


def test_create_checkin_awards_points_and_updates_streak(client, db_session):
    program = Program(name="Nutrition", description="desc", is_active=True)
    db_session.add(program)
    db_session.flush()
    habit = Habit(program_id=program.id, name="Drink water", points_per_completion=15)
    db_session.add(habit)
    db_session.commit()

    payload = {
        "user_id": 501,
        "habit_id": habit.id,
        "check_in_date": date.today().isoformat(),
        "notes": "Done",
    }

    response = client.post("/api/v1/check-ins/", json=payload)
    assert response.status_code == 201

    ledger = db_session.query(PointsLedger).filter(PointsLedger.user_id == 501).all()
    assert len(ledger) == 1
    assert ledger[0].points == 15

    streak = db_session.query(Streak).filter(Streak.user_id == 501).first()
    assert streak is not None
    assert streak.current_streak >= 1


def test_duplicate_checkin_rejected(client, db_session):
    program = Program(name="Sleep", description="desc", is_active=True)
    db_session.add(program)
    db_session.flush()
    habit = Habit(program_id=program.id, name="Sleep 8h", points_per_completion=10)
    db_session.add(habit)
    db_session.commit()

    payload = {"user_id": 1, "habit_id": habit.id, "check_in_date": date.today().isoformat()}
    assert client.post("/api/v1/check-ins/", json=payload).status_code == 201
    duplicate = client.post("/api/v1/check-ins/", json=payload)
    assert duplicate.status_code == 400
