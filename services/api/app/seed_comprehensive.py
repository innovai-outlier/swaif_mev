"""Comprehensive seed data with 30 patients, 10+ programs, badges, and streaks."""
import logging
import random
from datetime import date, datetime, timedelta
from app.database import SessionLocal
from app.models import (
    User,
    Program,
    Habit,
    Badge,
    Enrollment,
    CheckIn,
    PointsLedger,
    Streak,
)
from app.auth import get_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Brazilian names for realistic data
FIRST_NAMES = [
    "Ana", "João", "Maria", "Pedro", "Juliana", "Carlos", "Fernanda", "Lucas",
    "Camila", "Rafael", "Beatriz", "Gustavo", "Mariana", "Felipe", "Larissa",
    "Bruno", "Carolina", "Diego", "Isabela", "Thiago", "Gabriela", "Rodrigo",
    "Amanda", "Matheus", "Letícia", "Eduardo", "Patrícia", "André", "Renata", "Vinícius"
]

LAST_NAMES = [
    "Silva", "Santos", "Oliveira", "Souza", "Rodrigues", "Ferreira", "Alves",
    "Pereira", "Lima", "Gomes", "Costa", "Ribeiro", "Martins", "Carvalho",
    "Almeida", "Lopes", "Soares", "Fernandes", "Vieira", "Barbosa"
]


def seed_comprehensive_data():
    """Populate database with comprehensive test data."""
    db = SessionLocal()
    try:
        # Check if data already exists
        existing_programs = db.query(Program).count()
        if existing_programs > 5:
            logger.info("Database already has comprehensive data. Skipping.")
            return

        logger.info("Starting comprehensive database seed...")

        # ==================== USERS (PATIENTS) ====================
        logger.info("Creating 30 patient users...")
        patients = []
        for i in range(30):
            first_name = random.choice(FIRST_NAMES)
            last_name = random.choice(LAST_NAMES)
            full_name = f"{first_name} {last_name}"
            email = f"{first_name.lower()}.{last_name.lower()}{i+1}@paciente.com"

            patient = User(
                email=email,
                full_name=full_name,
                hashed_password=get_password_hash("paciente123"),  # Default password
                role="patient",
                is_active=True,
            )
            db.add(patient)
            patients.append(patient)

        db.flush()  # Get patient IDs
        logger.info(f"Created {len(patients)} patient users")

        # ==================== PROGRAMS ====================
        programs_data = [
            {
                "name": "Programa Lifestyle 30 Dias",
                "description": "Programa completo de medicina de estilo de vida com foco em hábitos diários saudáveis",
                "habits": [
                    ("Beber 2L de água", "Manter-se hidratado ao longo do dia", 10),
                    ("30min de exercício", "Atividade física moderada ou intensa", 20),
                    ("7-8h de sono", "Descanso adequado para recuperação", 15),
                    ("Meditar 10min", "Prática de mindfulness e redução de estresse", 15),
                ]
            },
            {
                "name": "Nutrição Consciente",
                "description": "Foco em alimentação saudável, mindful eating e controle de porções",
                "habits": [
                    ("5 porções de vegetais", "Consumir variedade de vegetais coloridos", 15),
                    ("Evitar açúcar refinado", "Reduzir consumo de açúcares processados", 10),
                    ("Comer devagar", "Mastigar bem e saborear cada refeição", 10),
                ]
            },
            {
                "name": "Gestão do Estresse",
                "description": "Técnicas para redução de estresse e melhora da saúde mental",
                "habits": [
                    ("Respiração profunda 3x", "Exercícios de respiração ao acordar, almoço e noite", 10),
                    ("Gratidão diária", "Registrar 3 coisas pelas quais é grato", 10),
                    ("Limitar redes sociais", "Máximo 30min por dia em redes sociais", 15),
                    ("Contato com natureza", "Passar tempo ao ar livre", 15),
                ]
            },
            {
                "name": "Sono Restaurador",
                "description": "Melhorar qualidade e consistência do sono",
                "habits": [
                    ("Rotina de sono consistente", "Dormir e acordar no mesmo horário", 15),
                    ("Tela desligada 1h antes", "Evitar telas azuis antes de dormir", 10),
                    ("Quarto escuro e fresco", "Ambiente ideal para sono", 10),
                    ("Chá relaxante", "Camomila ou valeriana antes de dormir", 5),
                ]
            },
            {
                "name": "Movimento Inteligente",
                "description": "Programa de atividade física progressiva e sustentável",
                "habits": [
                    ("10.000 passos", "Caminhar ao longo do dia", 20),
                    ("Alongamento matinal", "15min de alongamento ao acordar", 10),
                    ("Treino de força 3x", "Musculação ou peso corporal", 25),
                    ("Mobilidade articular", "Exercícios de amplitude de movimento", 10),
                ]
            },
            {
                "name": "Saúde Cardiovascular",
                "description": "Hábitos para fortalecer o coração e sistema circulatório",
                "habits": [
                    ("Cardio 30min", "Corrida, ciclismo ou natação moderada", 20),
                    ("Controle de sódio", "Reduzir sal na alimentação", 10),
                    ("Ômega-3 diário", "Suplemento ou peixes gordurosos", 10),
                    ("Medição de pressão", "Monitorar pressão arterial", 5),
                ]
            },
            {
                "name": "Detox Digital",
                "description": "Reduzir dependência tecnológica e melhorar foco",
                "habits": [
                    ("Manhã sem celular", "Primeira hora do dia sem telas", 15),
                    ("Modo avião ao dormir", "Desconexão completa durante sono", 10),
                    ("Refeições sem tela", "Comer com atenção plena", 10),
                    ("Leitura física 30min", "Livro ou revista em papel", 15),
                ]
            },
            {
                "name": "Fortalecimento Mental",
                "description": "Exercícios cognitivos e aprendizado contínuo",
                "habits": [
                    ("Aprender algo novo", "15min de estudo ou novo idioma", 15),
                    ("Jogo de raciocínio", "Xadrez, sudoku ou quebra-cabeça", 10),
                    ("Escrever diário", "Reflexão escrita sobre o dia", 10),
                    ("Conversa profunda", "Diálogo significativo com alguém", 15),
                ]
            },
            {
                "name": "Relações Saudáveis",
                "description": "Fortalecer conexões e comunicação interpessoal",
                "habits": [
                    ("Ligar para um amigo", "Contato genuíno com pessoa querida", 15),
                    ("Ato de bondade", "Ajudar alguém sem esperar retorno", 10),
                    ("Tempo em família", "Atividade de qualidade com família", 20),
                    ("Ouvir ativamente", "Praticar escuta sem interrupção", 10),
                ]
            },
            {
                "name": "Equilíbrio Financeiro",
                "description": "Hábitos para saúde financeira e redução de estresse monetário",
                "habits": [
                    ("Registrar gastos", "Anotar todas as despesas do dia", 10),
                    ("Poupar 10%", "Guardar percentual da renda", 15),
                    ("Evitar compra impulsiva", "Esperar 24h antes de comprar", 10),
                    ("Revisar orçamento", "Análise semanal das finanças", 15),
                ]
            },
            {
                "name": "Energia Vital",
                "description": "Maximizar energia física e mental ao longo do dia",
                "habits": [
                    ("Café da manhã nutritivo", "Proteína, fibras e gorduras saudáveis", 15),
                    ("Pausas de 5min", "Levantar e mover a cada hora", 10),
                    ("Hidratação constante", "Beber água regularmente", 10),
                    ("Power nap 20min", "Cochilo energizante se necessário", 10),
                ]
            },
            {
                "name": "Imunidade Forte",
                "description": "Fortalecer sistema imunológico naturalmente",
                "habits": [
                    ("Vitamina C diária", "Frutas cítricas ou suplemento", 10),
                    ("Probióticos", "Iogurte natural ou kefir", 10),
                    ("Sol 15min", "Vitamina D natural", 10),
                    ("Mãos higienizadas", "Lavar mãos regularmente", 5),
                ]
            },
        ]

        logger.info(f"Creating {len(programs_data)} programs...")
        programs = []
        for prog_data in programs_data:
            program = Program(
                name=prog_data["name"],
                description=prog_data["description"],
                is_active=True,
            )
            db.add(program)
            db.flush()

            # Create habits for this program
            for habit_name, habit_desc, points in prog_data["habits"]:
                habit = Habit(
                    program_id=program.id,
                    name=habit_name,
                    description=habit_desc,
                    points_per_completion=points,
                    is_active=True,
                )
                db.add(habit)

            programs.append(program)

        db.flush()
        logger.info(f"Created {len(programs)} programs with habits")

        # ==================== BADGES ====================
        badges_data = [
            ("Iniciante", "Primeiro check-in realizado", 10),
            ("Consistente", "7 dias consecutivos de check-ins", 50),
            ("Dedicado", "30 dias consecutivos", 100),
            ("Mestre", "100 check-ins totais", 200),
            ("Hidratação Expert", "30 dias bebendo água", 75),
            ("Fitness Warrior", "50 treinos completados", 150),
            ("Zen Master", "30 dias de meditação", 100),
            ("Nutricionista", "30 dias de alimentação saudável", 100),
            ("Madrugador", "15 dias acordando cedo", 50),
            ("Focado", "7 dias sem distrações digitais", 75),
            ("Social Butterfly", "Conectou-se com 10 amigos", 50),
            ("Financeiro Sábio", "30 dias controlando gastos", 100),
            ("Campeão", "Completou 3 programas", 250),
            ("Lenda", "500 check-ins totais", 500),
        ]

        logger.info(f"Creating {len(badges_data)} badges...")
        badges = []
        for badge_name, badge_desc, points_reward in badges_data:
            badge = Badge(
                name=badge_name,
                description=badge_desc,
                points_reward=points_reward,
            )
            db.add(badge)
            badges.append(badge)

        db.flush()
        logger.info(f"Created {len(badges)} badges")

        # ==================== ENROLLMENTS ====================
        logger.info("Creating enrollments for patients...")

        # Enroll patients in random programs (1-4 programs each)
        for patient in patients:
            num_programs = random.randint(1, 4)
            selected_programs = random.sample(programs, num_programs)

            for program in selected_programs:
                enrollment = Enrollment(
                    user_id=patient.id,
                    program_id=program.id,
                    is_active=True,
                    enrolled_at=datetime.utcnow() - timedelta(days=random.randint(1, 60)),
                )
                db.add(enrollment)

        db.flush()
        logger.info("Created enrollments for all patients")

        # ==================== CHECK-INS & STREAKS ====================
        logger.info("Creating check-ins, points, and streaks...")

        today = date.today()

        for patient in patients:
            # Get user's enrollments
            enrollments = db.query(Enrollment).filter(
                Enrollment.user_id == patient.id,
                Enrollment.is_active == True
            ).all()

            # Random activity level (some users more active than others)
            activity_factor = random.uniform(0.3, 0.95)  # 30-95% check-in rate

            for enrollment in enrollments:
                # Get habits for this program
                habits = db.query(Habit).filter(
                    Habit.program_id == enrollment.program_id,
                    Habit.is_active == True
                ).all()

                # Determine how many days back to create check-ins
                days_enrolled = (datetime.utcnow() - enrollment.enrolled_at).days
                days_to_simulate = min(days_enrolled, 60)  # Max 60 days history

                for habit in habits:
                    current_streak = 0
                    longest_streak = 0
                    last_checkin_date = None

                    for days_ago in range(days_to_simulate, -1, -1):
                        check_date = today - timedelta(days=days_ago)

                        # Random chance of check-in based on activity factor
                        if random.random() < activity_factor:
                            try:
                                check_in = CheckIn(
                                    user_id=patient.id,
                                    habit_id=habit.id,
                                    check_in_date=check_date,
                                    notes=f"Check-in automático - {habit.name}",
                                    created_at=datetime.combine(check_date, datetime.min.time()),
                                )
                                db.add(check_in)

                                # Award points
                                points = PointsLedger(
                                    user_id=patient.id,
                                    program_id=enrollment.program_id,
                                    points=habit.points_per_completion,
                                    event_type="check_in",
                                    event_reference_id=None,  # Will be set after flush
                                    description=f"Check-in: {habit.name}",
                                    created_at=datetime.combine(check_date, datetime.min.time()),
                                )
                                db.add(points)

                                # Update streak tracking
                                if last_checkin_date is None or (check_date - last_checkin_date).days == 1:
                                    current_streak += 1
                                else:
                                    current_streak = 1

                                longest_streak = max(longest_streak, current_streak)
                                last_checkin_date = check_date

                            except Exception as e:
                                # Skip duplicates
                                pass
                        else:
                            # Missed check-in, reset current streak
                            current_streak = 0

                    # Create streak record if there were any check-ins
                    if longest_streak > 0:
                        streak = Streak(
                            user_id=patient.id,
                            habit_id=habit.id,
                            current_streak=current_streak,
                            longest_streak=longest_streak,
                            last_check_in_date=last_checkin_date or today,
                        )
                        db.add(streak)

        db.flush()
        logger.info("Created check-ins, points ledger, and streaks")

        # ==================== AWARD SOME BADGES ====================
        logger.info("Awarding badges to deserving users...")

        # Award "Iniciante" badge to everyone with at least 1 check-in
        iniciante_badge = next(b for b in badges if b.name == "Iniciante")
        for patient in patients:
            checkin_count = db.query(CheckIn).filter(CheckIn.user_id == patient.id).count()
            if checkin_count > 0:
                from app.models import UserBadge
                user_badge = UserBadge(
                    user_id=patient.id,
                    badge_id=iniciante_badge.id,
                    awarded_at=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
                )
                db.add(user_badge)

                # Award points for badge
                points = PointsLedger(
                    user_id=patient.id,
                    program_id=None,
                    points=iniciante_badge.points_reward,
                    event_type="badge_earned",
                    event_reference_id=iniciante_badge.id,
                    description=f"Badge: {iniciante_badge.name}",
                    created_at=user_badge.awarded_at,
                )
                db.add(points)

        # Award "Consistente" to users with 7+ day streaks
        consistente_badge = next(b for b in badges if b.name == "Consistente")
        strong_streaks = db.query(Streak).filter(Streak.longest_streak >= 7).all()
        awarded_users = set()
        for streak in strong_streaks:
            if streak.user_id not in awarded_users:
                from app.models import UserBadge
                user_badge = UserBadge(
                    user_id=streak.user_id,
                    badge_id=consistente_badge.id,
                    awarded_at=datetime.utcnow() - timedelta(days=random.randint(1, 20)),
                )
                db.add(user_badge)

                points = PointsLedger(
                    user_id=streak.user_id,
                    program_id=None,
                    points=consistente_badge.points_reward,
                    event_type="badge_earned",
                    event_reference_id=consistente_badge.id,
                    description=f"Badge: {consistente_badge.name}",
                    created_at=user_badge.awarded_at,
                )
                db.add(points)
                awarded_users.add(streak.user_id)

        db.commit()
        logger.info("✅ Comprehensive database seed completed successfully!")
        logger.info(f"   📊 {len(programs)} programs created")
        logger.info(f"   🎯 {len(badges)} badges created")
        logger.info(f"   👥 30 patients with enrollments and activity")
        logger.info(f"   ✓ Check-ins, points, streaks, and badges awarded")

    except Exception as e:
        logger.error(f"❌ Error during seed: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_comprehensive_data()
