"""Pydantic schemas for request/response validation."""
from datetime import date, datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ============= Program Schemas =============
class ProgramBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    is_active: bool = True


class ProgramCreate(ProgramBase):
    pass


class ProgramUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class ProgramResponse(ProgramBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============= Habit Schemas =============
class HabitBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    points_per_completion: int = Field(default=10, ge=0)
    source_type: str = Field(default="manual", max_length=50)
    source_ref_id: Optional[int] = None
    target_metric_key: Optional[str] = Field(default=None, max_length=100)
    is_active: bool = True


class HabitCreate(HabitBase):
    program_id: int


class HabitUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    points_per_completion: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class HabitResponse(HabitBase):
    id: int
    program_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============= Enrollment Schemas =============
class EnrollmentBase(BaseModel):
    user_id: int
    program_id: int


class EnrollmentCreate(EnrollmentBase):
    pass


class EnrollmentResponse(EnrollmentBase):
    id: int
    enrolled_at: datetime
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============= CheckIn Schemas =============
class CheckInBase(BaseModel):
    habit_id: int
    check_in_date: date
    metric_key: Optional[str] = Field(default=None, max_length=100)
    value_numeric: Optional[float] = None
    value_text: Optional[str] = None
    notes: Optional[str] = None


class CheckInCreate(CheckInBase):
    user_id: int


class CheckInResponse(CheckInBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============= Points Ledger Schemas =============
class PointsLedgerBase(BaseModel):
    points: int
    event_type: str = Field(..., max_length=50)
    event_reference_id: Optional[int] = None
    description: Optional[str] = None


class PointsLedgerCreate(PointsLedgerBase):
    user_id: int
    program_id: Optional[int] = None


class PointsLedgerResponse(PointsLedgerBase):
    id: int
    user_id: int
    program_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


# ============= Badge Schemas =============
class BadgeBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=255)
    criteria: Optional[str] = None
    points_reward: int = Field(default=0, ge=0)


class BadgeCreate(BadgeBase):
    pass


class BadgeUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=255)
    criteria: Optional[str] = None
    points_reward: Optional[int] = Field(None, ge=0)


class BadgeResponse(BadgeBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============= User Badge Schemas =============
class UserBadgeCreate(BaseModel):
    user_id: int
    badge_id: int


class UserBadgeResponse(BaseModel):
    id: int
    user_id: int
    badge_id: int
    awarded_at: datetime
    badge: Optional[BadgeResponse] = None

    class Config:
        from_attributes = True


# ============= Streak Schemas =============
class StreakBase(BaseModel):
    current_streak: int = 0
    longest_streak: int = 0
    last_check_in_date: Optional[date] = None


class StreakResponse(StreakBase):
    id: int
    user_id: int
    habit_id: Optional[int]
    program_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============= Aggregate/Dashboard Schemas =============
class UserPointsBalance(BaseModel):
    user_id: int
    program_id: Optional[int]
    total_points: int
    transaction_count: int


class UserDashboard(BaseModel):
    user_id: int
    total_points: int
    active_programs: int
    total_check_ins: int
    current_streaks: int
    badges_earned: int


# ============= Protocol Schemas =============
class ProtocolTemplateBase(BaseModel):
    code: str
    name: str
    version: str
    description: Optional[str] = None
    is_active: bool = True
    default_program_id: Optional[int] = None


class ProtocolTemplateCreate(ProtocolTemplateBase):
    pass


class ProtocolTemplateUpdate(BaseModel):
    name: Optional[str] = None
    version: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    default_program_id: Optional[int] = None


class ProtocolTemplateOut(ProtocolTemplateBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ArtifactDefinitionOut(BaseModel):
    id: int
    artifact_key: str
    type: str
    name: str
    schema_json: Optional[Dict[str, Any]] = None
    scoring_json: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class ProtocolRunCreate(BaseModel):
    user_id: int
    template_code: str


class ProtocolRunOut(BaseModel):
    id: int
    user_id: int
    protocol_template_id: int
    status: str
    current_phase_id: Optional[int]
    started_at: datetime
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ArtifactInstanceCreate(BaseModel):
    payload_json: Dict[str, Any]
    source: Optional[str] = None


class ArtifactInstanceOut(BaseModel):
    id: int
    protocol_run_id: int
    artifact_definition_id: int
    collected_at: datetime
    payload_json: Optional[Dict[str, Any]]
    computed_json: Optional[Dict[str, Any]]
    source: Optional[str]

    class Config:
        from_attributes = True


class GenerateInterventionsResponse(BaseModel):
    generated_habit_ids: List[int]
    generated_count: int


class PhaseAdvanceResponse(BaseModel):
    advanced: bool
    current_phase: Optional[str]
