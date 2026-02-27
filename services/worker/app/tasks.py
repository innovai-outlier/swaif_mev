"""Background tasks for streaks, badges, and reminders."""
from __future__ import annotations

import json
import logging
from collections import defaultdict
from datetime import date, datetime, timedelta

from sqlalchemy import and_, func

from app.celery_app import celery_app
from app.database import SessionLocal
from app.models import (
    Badge,
    CheckIn,
    Enrollment,
    Habit,
    NotificationEvent,
    PointsLedger,
    RewardConfig,
    Streak,
    User,
    UserBadge,
)

logger = logging.getLogger(__name__)


class WorkerTaskError(RuntimeError):
    """Explicit task-level error for operational telemetry."""


def _log(event: str, **kwargs: object) -> None:
    logger.info(json.dumps({'event': event, **kwargs}, default=str))


def _load_reward_map(session) -> dict[str, int]:
    rows = session.query(RewardConfig.config_key, RewardConfig.config_value).all()
    return {key: value for key, value in rows}


def _calculate_streak_metrics(ordered_dates: list[date]) -> tuple[int, int, date | None]:
    if not ordered_dates:
        return 0, 0, None

    desc_dates = sorted(set(ordered_dates), reverse=True)
    current = 1
    for idx in range(1, len(desc_dates)):
        if (desc_dates[idx - 1] - desc_dates[idx]).days == 1:
            current += 1
        else:
            break

    asc_dates = sorted(desc_dates)
    longest = 1
    run = 1
    for idx in range(1, len(asc_dates)):
        if (asc_dates[idx] - asc_dates[idx - 1]).days == 1:
            run += 1
            longest = max(longest, run)
        else:
            run = 1

    return current, longest, desc_dates[0]


def _badge_qualified(badge: Badge, total_check_ins: int, max_streak: int) -> bool:
    name = (badge.name or '').lower()
    criteria = (badge.criteria or '').lower()

    if 'iniciante' in name or 'first' in criteria:
        return total_check_ins >= 1
    if 'consistente' in name or '7' in criteria:
        return max_streak >= 7
    if 'dedicado' in name or '30' in criteria:
        return max_streak >= 30
    if 'mestre' in name or '100' in criteria:
        return total_check_ins >= 100

    if 'streak' in criteria:
        numbers = [int(token) for token in criteria.split() if token.isdigit()]
        return max_streak >= max(numbers) if numbers else False

    if 'check-in' in criteria or 'check in' in criteria:
        numbers = [int(token) for token in criteria.split() if token.isdigit()]
        return total_check_ins >= max(numbers) if numbers else False

    return False


@celery_app.task(
    bind=True,
    name='app.tasks.recalculate_streaks',
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=300,
    retry_jitter=True,
    retry_kwargs={'max_retries': 5},
)
def recalculate_streaks(self) -> dict[str, int]:
    """Recalculate all habit streaks and add configured streak milestone points."""
    started_at = datetime.utcnow()
    session = SessionLocal()
    processed = 0
    milestones_awarded = 0
    try:
        reward_map = _load_reward_map(session)
        streak_bonus_rules = {
            3: reward_map.get('streak_3_days_bonus', 20),
            7: reward_map.get('streak_7_days_bonus', 50),
            14: reward_map.get('streak_14_days_bonus', 100),
            30: reward_map.get('streak_30_days_bonus', 250),
        }

        grouped_dates = defaultdict(list)
        for user_id, habit_id, check_in_date in session.query(
            CheckIn.user_id,
            CheckIn.habit_id,
            CheckIn.check_in_date,
        ).all():
            grouped_dates[(user_id, habit_id)].append(check_in_date)

        habits_map = dict(session.query(Habit.id, Habit.program_id).all())

        for (user_id, habit_id), dates in grouped_dates.items():
            current, longest, last_date = _calculate_streak_metrics(dates)
            streak = (
                session.query(Streak)
                .filter(and_(Streak.user_id == user_id, Streak.habit_id == habit_id))
                .one_or_none()
            )
            if streak is None:
                streak = Streak(
                    user_id=user_id,
                    habit_id=habit_id,
                    program_id=habits_map.get(habit_id),
                    current_streak=current,
                    longest_streak=longest,
                    last_check_in_date=last_date,
                )
                session.add(streak)
                session.flush()
            else:
                streak.current_streak = current
                streak.longest_streak = max(streak.longest_streak or 0, longest)
                streak.last_check_in_date = last_date

            for milestone, points in streak_bonus_rules.items():
                if current < milestone:
                    continue
                description = f'Streak milestone {milestone} days'
                already_awarded = (
                    session.query(PointsLedger.id)
                    .filter(
                        and_(
                            PointsLedger.user_id == user_id,
                            PointsLedger.event_type == 'streak_milestone',
                            PointsLedger.description == description,
                        )
                    )
                    .first()
                )
                if already_awarded:
                    continue

                session.add(
                    PointsLedger(
                        user_id=user_id,
                        program_id=streak.program_id,
                        points=points,
                        event_type='streak_milestone',
                        event_reference_id=streak.id,
                        description=description,
                    )
                )
                milestones_awarded += 1

            processed += 1

        session.commit()
        _log(
            'task.recalculate_streaks.completed',
            processed=processed,
            milestones_awarded=milestones_awarded,
            elapsed_seconds=(datetime.utcnow() - started_at).total_seconds(),
        )
        return {'processed': processed, 'milestones_awarded': milestones_awarded}
    except Exception as exc:
        session.rollback()
        _log('task.recalculate_streaks.failed', error=str(exc), attempt=self.request.retries + 1)
        raise WorkerTaskError('streak recalculation failed') from exc
    finally:
        session.close()


@celery_app.task(
    bind=True,
    name='app.tasks.assign_badges',
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=300,
    retry_jitter=True,
    retry_kwargs={'max_retries': 5},
)
def assign_badges(self) -> dict[str, int]:
    """Assign badges using check-in and streak criteria, then award points."""
    session = SessionLocal()
    awarded = 0
    try:
        badges = session.query(Badge).all()
        if not badges:
            _log('task.assign_badges.completed', awarded=0, reason='no_badges_configured')
            return {'awarded': 0}

        users = session.query(User.id).filter(User.is_active.is_(True)).all()
        for (user_id,) in users:
            total_check_ins = session.query(func.count(CheckIn.id)).filter(CheckIn.user_id == user_id).scalar() or 0
            max_streak = (
                session.query(func.max(Streak.longest_streak)).filter(Streak.user_id == user_id).scalar() or 0
            )

            for badge in badges:
                if not _badge_qualified(badge, total_check_ins, max_streak):
                    continue

                existing = (
                    session.query(UserBadge.id)
                    .filter(and_(UserBadge.user_id == user_id, UserBadge.badge_id == badge.id))
                    .first()
                )
                if existing:
                    continue

                user_badge = UserBadge(user_id=user_id, badge_id=badge.id)
                session.add(user_badge)
                session.flush()

                if badge.points_reward > 0:
                    session.add(
                        PointsLedger(
                            user_id=user_id,
                            points=badge.points_reward,
                            event_type='badge_earned',
                            event_reference_id=user_badge.id,
                            description=f'Badge earned: {badge.name}',
                        )
                    )
                awarded += 1

        session.commit()
        _log('task.assign_badges.completed', awarded=awarded)
        return {'awarded': awarded}
    except Exception as exc:
        session.rollback()
        _log('task.assign_badges.failed', error=str(exc), attempt=self.request.retries + 1)
        raise WorkerTaskError('badge assignment failed') from exc
    finally:
        session.close()


@celery_app.task(
    bind=True,
    name='app.tasks.dispatch_scheduled_reminders',
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=300,
    retry_jitter=True,
    retry_kwargs={'max_retries': 5},
)
def dispatch_scheduled_reminders(self) -> dict[str, int]:
    """Create reminder and streak-risk notification events for active users."""
    session = SessionLocal()
    reminders = 0
    streak_risk_alerts = 0
    today = date.today()
    try:
        active_users = (
            session.query(User.id)
            .join(Enrollment, Enrollment.user_id == User.id)
            .filter(and_(User.is_active.is_(True), Enrollment.is_active.is_(True)))
            .distinct()
            .all()
        )

        for (user_id,) in active_users:
            has_check_in_today = (
                session.query(CheckIn.id)
                .filter(and_(CheckIn.user_id == user_id, CheckIn.check_in_date == today))
                .first()
                is not None
            )
            if has_check_in_today:
                continue

            already_reminded = (
                session.query(NotificationEvent.id)
                .filter(
                    and_(
                        NotificationEvent.user_id == user_id,
                        NotificationEvent.event_type == 'check_in_reminder',
                        NotificationEvent.created_at >= datetime.combine(today, datetime.min.time()),
                    )
                )
                .first()
            )
            if not already_reminded:
                session.add(
                    NotificationEvent(
                        user_id=user_id,
                        event_type='check_in_reminder',
                        event_data=json.dumps({'date': today.isoformat(), 'channel': 'scheduled'}),
                    )
                )
                reminders += 1

            has_streak_yesterday = (
                session.query(Streak.id)
                .filter(
                    and_(
                        Streak.user_id == user_id,
                        Streak.current_streak > 0,
                        Streak.last_check_in_date == (today - timedelta(days=1)),
                    )
                )
                .first()
                is not None
            )
            if has_streak_yesterday:
                session.add(
                    NotificationEvent(
                        user_id=user_id,
                        event_type='streak_risk_alert',
                        event_data=json.dumps({'date': today.isoformat(), 'reason': 'streak_break_risk'}),
                    )
                )
                streak_risk_alerts += 1

        session.commit()
        _log(
            'task.dispatch_scheduled_reminders.completed',
            reminders=reminders,
            streak_risk_alerts=streak_risk_alerts,
        )
        return {'reminders': reminders, 'streak_risk_alerts': streak_risk_alerts}
    except Exception as exc:
        session.rollback()
        _log(
            'task.dispatch_scheduled_reminders.failed',
            error=str(exc),
            attempt=self.request.retries + 1,
        )
        raise WorkerTaskError('scheduled reminders failed') from exc
    finally:
        session.close()
