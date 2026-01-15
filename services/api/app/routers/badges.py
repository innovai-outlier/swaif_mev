"""Badges API endpoints."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models import Badge, UserBadge, PointsLedger
from app.schemas import BadgeCreate, BadgeUpdate, BadgeResponse, UserBadgeCreate, UserBadgeResponse

router = APIRouter(prefix="/api/v1/badges", tags=["badges"])


@router.get("/", response_model=List[BadgeResponse])
def list_badges(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all badges."""
    badges = db.query(Badge).offset(skip).limit(limit).all()
    return badges


@router.get("/{badge_id}", response_model=BadgeResponse)
def get_badge(badge_id: int, db: Session = Depends(get_db)):
    """Get a specific badge by ID."""
    badge = db.query(Badge).filter(Badge.id == badge_id).first()
    if not badge:
        raise HTTPException(status_code=404, detail="Badge not found")
    return badge


@router.post("/", response_model=BadgeResponse, status_code=status.HTTP_201_CREATED)
def create_badge(badge: BadgeCreate, db: Session = Depends(get_db)):
    """Create a new badge."""
    db_badge = Badge(**badge.model_dump())
    db.add(db_badge)
    db.commit()
    db.refresh(db_badge)
    return db_badge


@router.patch("/{badge_id}", response_model=BadgeResponse)
def update_badge(badge_id: int, badge_update: BadgeUpdate, db: Session = Depends(get_db)):
    """Update a badge."""
    db_badge = db.query(Badge).filter(Badge.id == badge_id).first()
    if not db_badge:
        raise HTTPException(status_code=404, detail="Badge not found")

    update_data = badge_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_badge, key, value)

    db.commit()
    db.refresh(db_badge)
    return db_badge


@router.post("/award", response_model=UserBadgeResponse, status_code=status.HTTP_201_CREATED)
def award_badge(award: UserBadgeCreate, db: Session = Depends(get_db)):
    """Award a badge to a user and grant points reward."""
    # Verify badge exists
    badge = db.query(Badge).filter(Badge.id == award.badge_id).first()
    if not badge:
        raise HTTPException(status_code=404, detail="Badge not found")

    try:
        # Create user badge award
        user_badge = UserBadge(**award.model_dump())
        db.add(user_badge)
        db.flush()

        # Award points if badge has points reward
        if badge.points_reward > 0:
            points_entry = PointsLedger(
                user_id=award.user_id,
                program_id=None,
                points=badge.points_reward,
                event_type="badge_earned",
                event_reference_id=user_badge.id,
                description=f"Badge earned: {badge.name}",
            )
            db.add(points_entry)

        db.commit()
        db.refresh(user_badge)

        # Load badge details
        user_badge.badge = badge
        return user_badge

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400, detail="Badge already awarded to this user"
        )
