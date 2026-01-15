"""SQLAlchemy models for Motor Clínico MVP."""
from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    Date,
    Numeric,
    Index,
)
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    """User accounts with role-based access."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="patient")  # "admin" or "patient"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Program(Base):
    """Gamification program container."""

    __tablename__ = "programs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    habits = relationship("Habit", back_populates="program", cascade="all, delete-orphan")
    enrollments = relationship("Enrollment", back_populates="program")


class Habit(Base):
    """Trackable behavior within a program."""

    __tablename__ = "habits"

    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("programs.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    points_per_completion = Column(Integer, default=10)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    program = relationship("Program", back_populates="habits")
    check_ins = relationship("CheckIn", back_populates="habit")


class Enrollment(Base):
    """User participation in a program."""

    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)  # Foreign key to user service/table
    program_id = Column(Integer, ForeignKey("programs.id"), nullable=False)
    enrolled_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    program = relationship("Program", back_populates="enrollments")

    # Indexes for fast lookups
    __table_args__ = (Index("idx_user_program", "user_id", "program_id", unique=True),)


class CheckIn(Base):
    """Daily habit completion record."""

    __tablename__ = "check_ins"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    habit_id = Column(Integer, ForeignKey("habits.id"), nullable=False)
    check_in_date = Column(Date, nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    habit = relationship("Habit", back_populates="check_ins")

    # Prevent duplicate check-ins for same habit on same day
    __table_args__ = (
        Index("idx_user_habit_date", "user_id", "habit_id", "check_in_date", unique=True),
    )


class PointsLedger(Base):
    """Event-sourced point transactions (never mutate a total column)."""

    __tablename__ = "points_ledger"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    program_id = Column(Integer, ForeignKey("programs.id"), nullable=True)
    points = Column(Integer, nullable=False)
    event_type = Column(
        String(50), nullable=False
    )  # e.g., "check_in", "badge_earned", "bonus"
    event_reference_id = Column(Integer)  # e.g., check_in.id or badge.id
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Index for efficient balance calculations
    __table_args__ = (Index("idx_user_created", "user_id", "created_at"),)


class Badge(Base):
    """Achievement awarded to users."""

    __tablename__ = "badges"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text)
    icon = Column(String(255))  # Icon URL or identifier
    criteria = Column(Text)  # JSON or text describing unlock criteria
    points_reward = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user_badges = relationship("UserBadge", back_populates="badge")


class UserBadge(Base):
    """User badge awards (junction table)."""

    __tablename__ = "user_badges"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    badge_id = Column(Integer, ForeignKey("badges.id"), nullable=False)
    awarded_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    badge = relationship("Badge", back_populates="user_badges")

    # Prevent duplicate awards
    __table_args__ = (Index("idx_user_badge", "user_id", "badge_id", unique=True),)


class NotificationEvent(Base):
    """Behavioral events for analytics."""

    __tablename__ = "notification_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    event_type = Column(String(50), nullable=False, index=True)
    event_data = Column(Text)  # JSON data
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class Streak(Base):
    """Consecutive days of habit/program completion."""

    __tablename__ = "streaks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    habit_id = Column(Integer, ForeignKey("habits.id"), nullable=True)
    program_id = Column(Integer, ForeignKey("programs.id"), nullable=True)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    last_check_in_date = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Index for fast lookups
    __table_args__ = (Index("idx_user_habit_program", "user_id", "habit_id", "program_id"),)


class RewardConfig(Base):
    """System-wide reward configuration for points allocation."""

    __tablename__ = "reward_config"

    id = Column(Integer, primary_key=True, index=True)
    config_key = Column(String(100), unique=True, nullable=False, index=True)
    config_value = Column(Integer, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

