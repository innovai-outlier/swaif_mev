"""Minimal ORM models used by the worker."""
from datetime import datetime

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    is_active = Column(Boolean, default=True)


class Habit(Base):
    __tablename__ = 'habits'

    id = Column(Integer, primary_key=True)
    program_id = Column(Integer, nullable=False)


class Enrollment(Base):
    __tablename__ = 'enrollments'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    program_id = Column(Integer, ForeignKey('programs.id'), nullable=False)
    is_active = Column(Boolean, default=True)


class CheckIn(Base):
    __tablename__ = 'check_ins'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    habit_id = Column(Integer, ForeignKey('habits.id'), nullable=False)
    check_in_date = Column(Date, nullable=False)


class Streak(Base):
    __tablename__ = 'streaks'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    habit_id = Column(Integer, nullable=True)
    program_id = Column(Integer, nullable=True)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    last_check_in_date = Column(Date)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Badge(Base):
    __tablename__ = 'badges'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    criteria = Column(Text)
    points_reward = Column(Integer, default=0)


class UserBadge(Base):
    __tablename__ = 'user_badges'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    badge_id = Column(Integer, ForeignKey('badges.id'), nullable=False)
    awarded_at = Column(DateTime, default=datetime.utcnow)


class PointsLedger(Base):
    __tablename__ = 'points_ledger'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    program_id = Column(Integer, nullable=True)
    points = Column(Integer, nullable=False)
    event_type = Column(String(50), nullable=False)
    event_reference_id = Column(Integer)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class NotificationEvent(Base):
    __tablename__ = 'notification_events'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    event_type = Column(String(50), nullable=False)
    event_data = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class RewardConfig(Base):
    __tablename__ = 'reward_config'

    id = Column(Integer, primary_key=True)
    config_key = Column(String(100), nullable=False)
    config_value = Column(Integer, nullable=False)
