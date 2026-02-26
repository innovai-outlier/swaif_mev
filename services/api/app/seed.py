"""Seed initial data for development and testing."""
import logging
from datetime import date, datetime, timedelta
from app.database import Base, SessionLocal, engine
from app.models import (
    Program,
    Habit,
    Badge,
    Enrollment,
    CheckIn,
    PointsLedger,
    Streak,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed_data():
    """Populate database with initial test data."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Check if data already exists
        existing_programs = db.query(Program).count()
        if existing_programs > 0:
            logger.info("Database already seeded. Skipping.")
            return

        logger.info("Starting database seed...")

        # Create Programs
        lifestyle_program = Program(
            name="Programa Lifestyle 30 Dias",
            description="Programa completo de medicina de estilo de vida com foco em hábitos diários",
            is_active=True,
        )
        db.add(lifestyle_program)
        db.flush()

        nutrition_program = Program(
            name="Nutrição Consciente",
            description="Foco em alimentação saudável e mindful eating",
            is_active=True,
        )
        db.add(nutrition_program)
        db.flush()

        # Create Habits for Lifestyle Program
        habits_lifestyle = [
            Habit(
                program_id=lifestyle_program.id,
                name="Hidratação (2L água/dia)",
                description="Beber pelo menos 2 litros de água por dia",
                points_per_completion=10,
            ),
            Habit(
                program_id=lifestyle_program.id,
                name="Exercício Físico (30min)",
                description="Mínimo de 30 minutos de atividade física",
                points_per_completion=20,
            ),
            Habit(
                program_id=lifestyle_program.id,
                name="Meditação (10min)",
                description="Prática diária de meditação ou mindfulness",
                points_per_completion=15,
            ),
            Habit(
                program_id=lifestyle_program.id,
                name="Sono de Qualidade (7-8h)",
                description="Dormir entre 7 e 8 horas por noite",
                points_per_completion=15,
            ),
        ]
        for habit in habits_lifestyle:
            db.add(habit)
        db.flush()

        # Create Habits for Nutrition Program
        habits_nutrition = [
            Habit(
                program_id=nutrition_program.id,
                name="5 Porções de Vegetais",
                description="Consumir pelo menos 5 porções de frutas e vegetais",
                points_per_completion=15,
            ),
            Habit(
                program_id=nutrition_program.id,
                name="Refeição Sem Tela",
                description="Fazer pelo menos uma refeição sem dispositivos eletrônicos",
                points_per_completion=10,
            ),
        ]
        for habit in habits_nutrition:
            db.add(habit)
        db.flush()

        # Create Badges
        badges = [
            Badge(
                name="Primeira Conquista",
                description="Complete seu primeiro check-in",
                points_reward=50,
                criteria="First check-in completed",
            ),
            Badge(
                name="Sequência de 7 Dias",
                description="Mantenha uma sequência de 7 dias consecutivos",
                points_reward=100,
                criteria="7-day streak achieved",
            ),
            Badge(
                name="Sequência de 30 Dias",
                description="Mantenha uma sequência de 30 dias consecutivos",
                points_reward=500,
                criteria="30-day streak achieved",
            ),
            Badge(
                name="Mestre da Hidratação",
                description="Complete o hábito de hidratação 30 vezes",
                points_reward=200,
                criteria="30 hydration check-ins",
            ),
        ]
        for badge in badges:
            db.add(badge)
        db.flush()

        # Create test users enrollments (user_id 1 and 2)
        enrollments = [
            Enrollment(user_id=1, program_id=lifestyle_program.id, is_active=True),
            Enrollment(user_id=2, program_id=lifestyle_program.id, is_active=True),
            Enrollment(user_id=2, program_id=nutrition_program.id, is_active=True),
        ]
        for enrollment in enrollments:
            db.add(enrollment)
        db.flush()

        # Create some check-ins for user 1 (last 7 days)
        today = date.today()
        for i in range(7):
            check_in_date = today - timedelta(days=i)
            for habit in habits_lifestyle[:2]:  # First 2 habits
                check_in = CheckIn(
                    user_id=1,
                    habit_id=habit.id,
                    check_in_date=check_in_date,
                    notes=f"Check-in automático de seed - dia {i + 1}",
                )
                db.add(check_in)

                # Add points to ledger
                points = PointsLedger(
                    user_id=1,
                    program_id=lifestyle_program.id,
                    points=habit.points_per_completion,
                    event_type="check_in",
                    event_reference_id=None,  # Will be set after flush
                    description=f"Check-in: {habit.name}",
                )
                db.add(points)
        db.flush()

        # Create streaks for user 1
        for habit in habits_lifestyle[:2]:
            streak = Streak(
                user_id=1,
                habit_id=habit.id,
                program_id=lifestyle_program.id,
                current_streak=7,
                longest_streak=7,
                last_check_in_date=today,
            )
            db.add(streak)

        db.commit()
        logger.info("✅ Database seeded successfully!")
        logger.info(f"   - {len([lifestyle_program, nutrition_program])} programs created")
        logger.info(f"   - {len(habits_lifestyle + habits_nutrition)} habits created")
        logger.info(f"   - {len(badges)} badges created")
        logger.info(f"   - {len(enrollments)} enrollments created")
        logger.info("   - Sample check-ins and points for user 1")

    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
