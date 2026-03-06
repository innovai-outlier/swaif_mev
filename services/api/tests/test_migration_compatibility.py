from sqlalchemy import inspect

from app.models import Base


def test_schema_can_be_created_for_fresh_install(db_session):
    inspector = inspect(db_session.bind)
    tables = set(inspector.get_table_names())

    expected = {
        "users",
        "programs",
        "habits",
        "enrollments",
        "check_ins",
        "points_ledger",
        "badges",
        "user_badges",
        "notification_events",
        "streaks",
        "reward_config",
    }
    assert expected.issubset(tables)


def test_unique_indexes_preserved_for_existing_data(db_session):
    inspector = inspect(db_session.bind)
    enrollment_indexes = {idx["name"] for idx in inspector.get_indexes("enrollments")}
    checkin_indexes = {idx["name"] for idx in inspector.get_indexes("check_ins")}

    assert "idx_user_program" in enrollment_indexes
    assert "idx_user_habit_date" in checkin_indexes
    assert len(Base.metadata.tables) >= 10
