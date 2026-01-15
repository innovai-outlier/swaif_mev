"""Seed script to create default admin user."""
import logging
from app.database import SessionLocal
from app.models import User
from app.auth import get_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed_admin_user():
    """Create default admin user if not exists."""
    db = SessionLocal()
    try:
        # Check if admin already exists
        admin = db.query(User).filter(User.email == "admin@mev.com").first()
        if admin:
            logger.info("Admin user already exists")
            return

        # Create admin user
        admin_user = User(
            email="admin@mev.com",
            full_name="Administrador",
            hashed_password=get_password_hash("admin123"),  # Change this in production!
            role="admin",
            is_active=True,
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

        logger.info("✅ Admin user created successfully!")
        logger.info(f"   Email: admin@mev.com")
        logger.info(f"   Password: admin123")
        logger.info(f"   ⚠️  CHANGE PASSWORD IN PRODUCTION!")

    except Exception as e:
        logger.error(f"Error creating admin user: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    logger.info("Starting admin user seed...")
    seed_admin_user()
    logger.info("Admin user seed completed!")
