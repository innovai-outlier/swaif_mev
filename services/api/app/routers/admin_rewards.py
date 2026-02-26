"""Admin router for reward configuration management."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from app.database import get_db
from app.models import RewardConfig, User
from app.auth import require_admin

router = APIRouter(prefix="/api/v1/admin/rewards", tags=["admin", "rewards"])


class RewardConfigItem(BaseModel):
    """Schema for reward configuration item."""
    config_key: str
    config_value: int
    description: str

    class Config:
        from_attributes = True


class RewardConfigUpdate(BaseModel):
    """Schema for updating reward configurations."""
    configs: List[RewardConfigItem]


# Default reward configuration
DEFAULT_REWARDS = [
    {
        "config_key": "check_in_points",
        "config_value": 10,
        "description": "Pontos por completar um check-in diário"
    },
    {
        "config_key": "streak_3_days_bonus",
        "config_value": 20,
        "description": "Bônus por manter 3 dias consecutivos"
    },
    {
        "config_key": "streak_7_days_bonus",
        "config_value": 50,
        "description": "Bônus por manter 7 dias consecutivos"
    },
    {
        "config_key": "streak_14_days_bonus",
        "config_value": 100,
        "description": "Bônus por manter 14 dias consecutivos"
    },
    {
        "config_key": "streak_30_days_bonus",
        "config_value": 250,
        "description": "Bônus por manter 30 dias consecutivos"
    },
    {
        "config_key": "program_completion_bonus",
        "config_value": 500,
        "description": "Bônus por completar um programa inteiro"
    },
    {
        "config_key": "first_check_in_bonus",
        "config_value": 25,
        "description": "Bônus pelo primeiro check-in em um programa"
    },
    {
        "config_key": "perfect_week_bonus",
        "config_value": 100,
        "description": "Bônus por completar todos os hábitos durante 7 dias"
    }
]


@router.get("/config", response_model=List[RewardConfigItem])
def get_reward_config(
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
):
    """Get current reward configuration."""
    configs = db.query(RewardConfig).all()
    
    # If no config exists, initialize with defaults
    if not configs:
        for default in DEFAULT_REWARDS:
            config = RewardConfig(**default)
            db.add(config)
        db.commit()
        configs = db.query(RewardConfig).all()
    
    return configs


@router.put("/config", response_model=List[RewardConfigItem])
def update_reward_config(
    config_update: RewardConfigUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
):
    """Update reward configuration."""
    updated_configs = []
    
    for config_item in config_update.configs:
        # Find existing config
        existing = db.query(RewardConfig).filter(
            RewardConfig.config_key == config_item.config_key
        ).first()
        
        if existing:
            # Update existing
            existing.config_value = config_item.config_value
            existing.description = config_item.description
            updated_configs.append(existing)
        else:
            # Create new
            new_config = RewardConfig(
                config_key=config_item.config_key,
                config_value=config_item.config_value,
                description=config_item.description,
            )
            db.add(new_config)
            updated_configs.append(new_config)
    
    db.commit()
    
    # Refresh all to get updated timestamps
    for config in updated_configs:
        db.refresh(config)
    
    return updated_configs


@router.post("/config/reset", response_model=List[RewardConfigItem])
def reset_reward_config(
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
):
    """Reset reward configuration to defaults."""
    # Delete all existing configs
    db.query(RewardConfig).delete()
    
    # Create default configs
    configs = []
    for default in DEFAULT_REWARDS:
        config = RewardConfig(**default)
        db.add(config)
        configs.append(config)
    
    db.commit()
    
    # Refresh to get IDs and timestamps
    for config in configs:
        db.refresh(config)
    
    return configs
