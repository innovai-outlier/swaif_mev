"""User dashboard and analytics endpoints."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import (
    PointsLedger,
    Enrollment,
    CheckIn,
    Streak,
    UserBadge,
    Badge,
)
from app.schemas import (
    UserPointsBalance,
    UserDashboard,
    StreakResponse,
    UserBadgeResponse,
    PointsLedgerResponse,
)

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.get("/{user_id}/points", response_model=UserPointsBalance)
def get_user_points(user_id: int, program_id: int = None, db: Session = Depends(get_db)):
    """Get total points for a user, optionally filtered by program."""
    query = db.query(
        func.sum(PointsLedger.points).label("total_points"),
        func.count(PointsLedger.id).label("transaction_count"),
    ).filter(PointsLedger.user_id == user_id)

    if program_id is not None:
        query = query.filter(PointsLedger.program_id == program_id)

    result = query.first()

    return UserPointsBalance(
        user_id=user_id,
        program_id=program_id,
        total_points=result.total_points or 0,
        transaction_count=result.transaction_count or 0,
    )


@router.get("/{user_id}/points/history", response_model=List[PointsLedgerResponse])
def get_user_points_history(
    user_id: int,
    program_id: int = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Get points transaction history for a user."""
    query = db.query(PointsLedger).filter(PointsLedger.user_id == user_id)

    if program_id is not None:
        query = query.filter(PointsLedger.program_id == program_id)

    transactions = (
        query.order_by(PointsLedger.created_at.desc()).offset(skip).limit(limit).all()
    )
    return transactions


@router.get("/{user_id}/streaks", response_model=List[StreakResponse])
def get_user_streaks(user_id: int, db: Session = Depends(get_db)):
    """Get all active streaks for a user."""
    streaks = db.query(Streak).filter(Streak.user_id == user_id).all()
    return streaks


@router.get("/{user_id}/badges", response_model=List[UserBadgeResponse])
def get_user_badges(user_id: int, db: Session = Depends(get_db)):
    """Get all badges earned by a user."""
    user_badges = (
        db.query(UserBadge)
        .filter(UserBadge.user_id == user_id)
        .order_by(UserBadge.awarded_at.desc())
        .all()
    )

    # Eager load badge details
    for ub in user_badges:
        ub.badge = db.query(Badge).filter(Badge.id == ub.badge_id).first()

    return user_badges


@router.get("/{user_id}/dashboard", response_model=UserDashboard)
def get_user_dashboard(user_id: int, db: Session = Depends(get_db)):
    """Get comprehensive dashboard data for a user."""
    # Total points
    points_result = (
        db.query(func.sum(PointsLedger.points))
        .filter(PointsLedger.user_id == user_id)
        .scalar()
    )

    # Active programs
    active_programs = (
        db.query(func.count(Enrollment.id))
        .filter(Enrollment.user_id == user_id, Enrollment.is_active == True)
        .scalar()
    )

    # Total check-ins
    total_check_ins = (
        db.query(func.count(CheckIn.id)).filter(CheckIn.user_id == user_id).scalar()
    )

    # Current active streaks (streak > 0)
    current_streaks = (
        db.query(func.count(Streak.id))
        .filter(Streak.user_id == user_id, Streak.current_streak > 0)
        .scalar()
    )

    # Badges earned
    badges_earned = (
        db.query(func.count(UserBadge.id)).filter(UserBadge.user_id == user_id).scalar()
    )

    return UserDashboard(
        user_id=user_id,
        total_points=points_result or 0,
        active_programs=active_programs or 0,
        total_check_ins=total_check_ins or 0,
        current_streaks=current_streaks or 0,
        badges_earned=badges_earned or 0,
    )
