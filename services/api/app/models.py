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
    JSON,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.database import Base


json_type = JSON().with_variant(JSONB, "postgresql")


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
    source_type = Column(String(50), nullable=False, default="manual")
    source_ref_id = Column(Integer, nullable=True)
    target_metric_key = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    program = relationship("Program", back_populates="habits")
    check_ins = relationship("CheckIn", back_populates="habit")
    protocol_generated_items = relationship("ProtocolGeneratedItem", back_populates="habit")

    __table_args__ = (
        Index("idx_habits_program_source", "program_id", "source_type", "source_ref_id"),
    )


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
    metric_key = Column(String(100), nullable=True)
    value_numeric = Column(Numeric, nullable=True)
    value_text = Column(Text, nullable=True)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    habit = relationship("Habit", back_populates="check_ins")

    # Prevent duplicate check-ins for same habit on same day
    __table_args__ = (
        Index("idx_user_habit_date", "user_id", "habit_id", "check_in_date", unique=True),
        Index("idx_checkins_user_metric_date", "user_id", "metric_key", "check_in_date"),
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


class ProtocolTemplate(Base):
    """Versioned clinical protocol template."""

    __tablename__ = "protocol_templates"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(100), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False)
    version = Column(String(50), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    default_program_id = Column(Integer, ForeignKey("programs.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    phases = relationship("ProtocolPhase", back_populates="protocol_template", cascade="all, delete-orphan")
    artifact_definitions = relationship(
        "ArtifactDefinition", back_populates="protocol_template", cascade="all, delete-orphan"
    )
    intervention_templates = relationship(
        "InterventionTemplate", back_populates="protocol_template", cascade="all, delete-orphan"
    )


class ProtocolPhase(Base):
    """Ordered protocol phase definition."""

    __tablename__ = "protocol_phases"

    id = Column(Integer, primary_key=True, index=True)
    protocol_template_id = Column(Integer, ForeignKey("protocol_templates.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    phase_key = Column(String(50), nullable=False)
    phase_order = Column(Integer, nullable=False)
    entry_criteria_json = Column(json_type, nullable=True)
    exit_criteria_json = Column(json_type, nullable=True)

    protocol_template = relationship("ProtocolTemplate", back_populates="phases")
    runs = relationship("ProtocolRun", back_populates="current_phase")

    __table_args__ = (
        Index("idx_protocol_phase_template_order", "protocol_template_id", "phase_order", unique=True),
    )


class ArtifactDefinition(Base):
    """Definitions for protocol artifacts/questionnaires/labs."""

    __tablename__ = "artifact_definitions"

    id = Column(Integer, primary_key=True, index=True)
    protocol_template_id = Column(Integer, ForeignKey("protocol_templates.id"), nullable=False, index=True)
    artifact_key = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)
    name = Column(String(255), nullable=False)
    schema_json = Column(json_type, nullable=True)
    scoring_json = Column(json_type, nullable=True)

    protocol_template = relationship("ProtocolTemplate", back_populates="artifact_definitions")
    instances = relationship("ArtifactInstance", back_populates="artifact_definition")

    __table_args__ = (
        Index("idx_artifact_definition_template_key", "protocol_template_id", "artifact_key", unique=True),
    )


class ProtocolRun(Base):
    """Protocol execution instance for a patient."""

    __tablename__ = "protocol_runs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    protocol_template_id = Column(Integer, ForeignKey("protocol_templates.id"), nullable=False, index=True)
    status = Column(String(50), nullable=False, default="active")
    current_phase_id = Column(Integer, ForeignKey("protocol_phases.id"), nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    protocol_template = relationship("ProtocolTemplate")
    current_phase = relationship("ProtocolPhase", back_populates="runs")
    artifact_instances = relationship("ArtifactInstance", back_populates="protocol_run", cascade="all, delete-orphan")
    generated_items = relationship("ProtocolGeneratedItem", back_populates="protocol_run", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_protocol_runs_user_status", "user_id", "status"),
    )


class ArtifactInstance(Base):
    """Collected artifact payload instances for a protocol run."""

    __tablename__ = "artifact_instances"

    id = Column(Integer, primary_key=True, index=True)
    protocol_run_id = Column(Integer, ForeignKey("protocol_runs.id"), nullable=False, index=True)
    artifact_definition_id = Column(Integer, ForeignKey("artifact_definitions.id"), nullable=False, index=True)
    collected_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    payload_json = Column(json_type, nullable=True)
    computed_json = Column(json_type, nullable=True)
    source = Column(String(50), nullable=True)

    protocol_run = relationship("ProtocolRun", back_populates="artifact_instances")
    artifact_definition = relationship("ArtifactDefinition", back_populates="instances")

    __table_args__ = (
        Index(
            "idx_artifact_instances_run_definition_collected",
            "protocol_run_id",
            "artifact_definition_id",
            "collected_at",
        ),
    )


class InterventionTemplate(Base):
    """Protocol intervention templates used to generate executable actions."""

    __tablename__ = "intervention_templates"

    id = Column(Integer, primary_key=True, index=True)
    protocol_template_id = Column(Integer, ForeignKey("protocol_templates.id"), nullable=False, index=True)
    intervention_key = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    habit_blueprint_json = Column(json_type, nullable=True)
    activation_rules_json = Column(json_type, nullable=True)

    protocol_template = relationship("ProtocolTemplate", back_populates="intervention_templates")
    generated_items = relationship("ProtocolGeneratedItem", back_populates="intervention_template")

    __table_args__ = (
        Index("idx_intervention_template_key", "protocol_template_id", "intervention_key", unique=True),
    )


class ProtocolGeneratedItem(Base):
    """Track entities generated from interventions for a protocol run."""

    __tablename__ = "protocol_generated_items"

    id = Column(Integer, primary_key=True, index=True)
    protocol_run_id = Column(Integer, ForeignKey("protocol_runs.id"), nullable=False, index=True)
    intervention_template_id = Column(Integer, ForeignKey("intervention_templates.id"), nullable=False, index=True)
    generated_habit_id = Column(Integer, ForeignKey("habits.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    protocol_run = relationship("ProtocolRun", back_populates="generated_items")
    intervention_template = relationship("InterventionTemplate", back_populates="generated_items")
    habit = relationship("Habit", back_populates="protocol_generated_items")
