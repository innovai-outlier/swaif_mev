"""Admin analytics endpoints for system-wide metrics."""
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, cast, Date
from datetime import datetime, timedelta

from app.database import get_db
from app.auth import require_admin
from app.models import (
    User,
    Program,
    Enrollment,
    CheckIn,
    PointsLedger,
    UserBadge,
    Badge,
)

router = APIRouter(prefix="/api/v1/admin/analytics", tags=["admin", "analytics"])


@router.get("/overview", dependencies=[Depends(require_admin)])
def get_analytics_overview(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get system-wide analytics overview.

    Returns key metrics:
    - Total users (patients)
    - Total programs
    - Active programs
    - Total check-ins
    - Total points awarded
    - Average engagement rate
    """
    # Total patients
    total_patients = db.query(User).filter(User.role == "patient").count()

    # Total and active programs
    total_programs = db.query(Program).count()
    active_programs = db.query(Program).filter(Program.is_active).count()

    # Total check-ins
    total_checkins = db.query(CheckIn).count()

    # Total points awarded
    total_points = db.query(func.sum(PointsLedger.points)).scalar() or 0

    # Total enrollments
    total_enrollments = db.query(Enrollment).filter(Enrollment.is_active).count()

    # Total badges awarded
    total_badges_awarded = db.query(UserBadge).count()

    # Check-ins in last 7 days
    week_ago = datetime.utcnow() - timedelta(days=7)
    checkins_last_week = (
        db.query(CheckIn)
        .filter(CheckIn.created_at >= week_ago)
        .count()
    )

    # Check-ins in last 30 days
    month_ago = datetime.utcnow() - timedelta(days=30)
    checkins_last_month = (
        db.query(CheckIn)
        .filter(CheckIn.created_at >= month_ago)
        .count()
    )

    # Average engagement (check-ins per active enrollment per week)
    avg_checkins_per_enrollment = (
        (checkins_last_week / total_enrollments * 100)
        if total_enrollments > 0
        else 0
    )

    # Most active users (top 5 by check-ins in last 30 days)
    top_users = (
        db.query(
            CheckIn.user_id,
            User.full_name,
            func.count(CheckIn.id).label("checkin_count")
        )
        .join(User, User.id == CheckIn.user_id)
        .filter(CheckIn.created_at >= month_ago)
        .group_by(CheckIn.user_id, User.full_name)
        .order_by(func.count(CheckIn.id).desc())
        .limit(5)
        .all()
    )

    # Most popular programs (by enrollment count)
    top_programs = (
        db.query(
            Program.id,
            Program.name,
            func.count(Enrollment.id).label("enrollment_count")
        )
        .join(Enrollment, Enrollment.program_id == Program.id)
        .filter(Enrollment.is_active)
        .group_by(Program.id, Program.name)
        .order_by(func.count(Enrollment.id).desc())
        .limit(5)
        .all()
    )

    return {
        "overview": {
            "total_patients": total_patients,
            "total_programs": total_programs,
            "active_programs": active_programs,
            "total_checkins": total_checkins,
            "total_points_awarded": int(total_points),
            "total_enrollments": total_enrollments,
            "total_badges_awarded": total_badges_awarded,
        },
        "recent_activity": {
            "checkins_last_7_days": checkins_last_week,
            "checkins_last_30_days": checkins_last_month,
            "avg_engagement_rate": round(avg_checkins_per_enrollment, 1),
        },
        "top_performers": {
            "most_active_users": [
                {
                    "user_id": user.user_id,
                    "full_name": user.full_name,
                    "checkin_count": user.checkin_count,
                }
                for user in top_users
            ],
            "most_popular_programs": [
                {
                    "program_id": prog.id,
                    "program_name": prog.name,
                    "enrollment_count": prog.enrollment_count,
                }
                for prog in top_programs
            ],
        },
    }


@router.get("/engagement-trends", dependencies=[Depends(require_admin)])
def get_engagement_trends(days: int = 30, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get daily engagement trends for the specified time period.

    Args:
        days: Number of days to look back (default: 30)

    Returns:
        Daily check-in counts and unique active users
    """
    if days > 365:
        raise HTTPException(status_code=400, detail="Maximum 365 days allowed")

    start_date = datetime.utcnow() - timedelta(days=days)

    # Daily check-ins
    daily_checkins = (
        db.query(
            cast(CheckIn.check_in_date, Date).label("date"),
            func.count(CheckIn.id).label("count")
        )
        .filter(CheckIn.created_at >= start_date)
        .group_by(cast(CheckIn.check_in_date, Date))
        .order_by(cast(CheckIn.check_in_date, Date))
        .all()
    )

    # Daily unique active users
    daily_users = (
        db.query(
            cast(CheckIn.check_in_date, Date).label("date"),
            func.count(func.distinct(CheckIn.user_id)).label("unique_users")
        )
        .filter(CheckIn.created_at >= start_date)
        .group_by(cast(CheckIn.check_in_date, Date))
        .order_by(cast(CheckIn.check_in_date, Date))
        .all()
    )

    return {
        "period_days": days,
        "start_date": start_date.date().isoformat(),
        "end_date": datetime.utcnow().date().isoformat(),
        "daily_checkins": [
            {"date": str(row.date), "count": row.count}
            for row in daily_checkins
        ],
        "daily_active_users": [
            {"date": str(row.date), "unique_users": row.unique_users}
            for row in daily_users
        ],
    }


@router.get("/program-performance", dependencies=[Depends(require_admin)])
def get_program_performance(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get detailed performance metrics for all programs."""
    programs = db.query(Program).filter(Program.is_active).all()

    results = []
    for program in programs:
        # Enrollment count
        enrollment_count = (
            db.query(Enrollment)
            .filter(
                Enrollment.program_id == program.id,
                Enrollment.is_active
            )
            .count()
        )

        # Total check-ins for this program
        checkin_count = (
            db.query(CheckIn)
            .join(Enrollment, and_(
                Enrollment.user_id == CheckIn.user_id,
                Enrollment.program_id == program.id
            ))
            .count()
        )

        # Total points awarded
        points_awarded = (
            db.query(func.sum(PointsLedger.points))
            .filter(PointsLedger.program_id == program.id)
            .scalar() or 0
        )

        # Average check-ins per enrollment
        avg_checkins = round(checkin_count / enrollment_count, 1) if enrollment_count > 0 else 0

        results.append({
            "program_id": program.id,
            "program_name": program.name,
            "enrollment_count": enrollment_count,
            "total_checkins": checkin_count,
            "total_points_awarded": int(points_awarded),
            "avg_checkins_per_enrollment": avg_checkins,
        })

    # Sort by enrollment count
    results.sort(key=lambda x: x["enrollment_count"], reverse=True)

    return {"programs": results}


@router.get("/badge-statistics", dependencies=[Depends(require_admin)])
def get_badge_statistics(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get statistics about badge awards."""
    # Total badges defined
    total_badges = db.query(Badge).count()

    # Badge award counts
    badge_awards = (
        db.query(
            Badge.id,
            Badge.name,
            Badge.description,
            Badge.points_reward,
            func.count(UserBadge.id).label("award_count")
        )
        .outerjoin(UserBadge, UserBadge.badge_id == Badge.id)
        .group_by(Badge.id, Badge.name, Badge.description, Badge.points_reward)
        .order_by(func.count(UserBadge.id).desc())
        .all()
    )

    return {
        "total_badges_defined": total_badges,
        "total_badges_awarded": db.query(UserBadge).count(),
        "badge_details": [
            {
                "badge_id": badge.id,
                "badge_name": badge.name,
                "description": badge.description,
                "points_reward": badge.points_reward,
                "times_awarded": badge.award_count,
            }
            for badge in badge_awards
        ],
    }
