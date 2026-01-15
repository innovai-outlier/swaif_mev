"""Admin router for badge management."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel
from typing import List, Optional
from app.database import get_db
from app.models import Badge, User
from app.auth import require_admin

router = APIRouter(prefix="/api/v1/admin/badges", tags=["admin", "badges"])


class BadgeCreate(BaseModel):
    """Schema for creating a badge."""
    name: str
    description: Optional[str] = None
    icon: Optional[str] = "🏆"
    criteria: Optional[str] = None
    points_reward: int = 0


class BadgeUpdate(BaseModel):
    """Schema for updating a badge."""
    name: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    criteria: Optional[str] = None
    points_reward: Optional[int] = None


class BadgeResponse(BaseModel):
    """Schema for badge response."""
    id: int
    name: str
    description: Optional[str]
    icon: Optional[str]
    criteria: Optional[str]
    points_reward: int

    class Config:
        from_attributes = True


@router.get("/", response_model=List[BadgeResponse])
def list_badges(
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
):
    """List all badges (admin only)."""
    badges = db.query(Badge).order_by(Badge.id).all()
    return badges


@router.get("/{badge_id}", response_model=BadgeResponse)
def get_badge(
    badge_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
):
    """Get a specific badge by ID (admin only)."""
    badge = db.query(Badge).filter(Badge.id == badge_id).first()
    if not badge:
        raise HTTPException(status_code=404, detail="Badge not found")
    return badge


@router.post("/", response_model=BadgeResponse, status_code=status.HTTP_201_CREATED)
def create_badge(
    badge: BadgeCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
):
    """Create a new badge (admin only)."""
    try:
        db_badge = Badge(**badge.model_dump())
        db.add(db_badge)
        db.commit()
        db.refresh(db_badge)
        return db_badge
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Badge with this name already exists",
        )


@router.put("/{badge_id}", response_model=BadgeResponse)
def update_badge(
    badge_id: int,
    badge_update: BadgeUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
):
    """Update a badge (admin only)."""
    db_badge = db.query(Badge).filter(Badge.id == badge_id).first()
    if not db_badge:
        raise HTTPException(status_code=404, detail="Badge not found")

    update_data = badge_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_badge, key, value)

    try:
        db.commit()
        db.refresh(db_badge)
        return db_badge
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Badge with this name already exists",
        )


@router.delete("/{badge_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_badge(
    badge_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
):
    """Delete a badge (admin only)."""
    db_badge = db.query(Badge).filter(Badge.id == badge_id).first()
    if not db_badge:
        raise HTTPException(status_code=404, detail="Badge not found")

    # Check if badge has been awarded to any users
    from app.models import UserBadge
    awarded_count = db.query(UserBadge).filter(UserBadge.badge_id == badge_id).count()
    
    if awarded_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete badge: it has been awarded to {awarded_count} user(s)",
        )

    db.delete(db_badge)
    db.commit()
    return None
