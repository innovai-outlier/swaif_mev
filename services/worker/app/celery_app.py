"""Celery app and beat schedule configuration."""
from celery import Celery
from celery.schedules import crontab
from kombu import Queue

from app.config import settings


def _crontab_from_expr(expr: str) -> crontab:
    minute, hour, day_of_month, month_of_year, day_of_week = expr.split()
    return crontab(
        minute=minute,
        hour=hour,
        day_of_month=day_of_month,
        month_of_year=month_of_year,
        day_of_week=day_of_week,
    )


celery_app = Celery(
    'mev_worker',
    broker=settings.broker_url,
    backend=settings.result_backend,
)

celery_app.conf.update(
    timezone=settings.celery_timezone,
    enable_utc=True,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    task_default_queue='default',
    task_queues=(
        Queue('default'),
        Queue('maintenance'),
        Queue('notifications'),
    ),
    beat_schedule={
        'recalculate-streaks-daily': {
            'task': 'app.tasks.recalculate_streaks',
            'schedule': _crontab_from_expr(settings.streak_recalc_cron),
            'options': {'queue': 'maintenance'},
        },
        'assign-badges-periodic': {
            'task': 'app.tasks.assign_badges',
            'schedule': _crontab_from_expr(settings.badge_assign_cron),
            'options': {'queue': 'maintenance'},
        },
        'dispatch-reminders': {
            'task': 'app.tasks.dispatch_scheduled_reminders',
            'schedule': _crontab_from_expr(settings.reminder_cron),
            'options': {'queue': 'notifications'},
        },
    },
)

celery_app.autodiscover_tasks(['app'])

app = celery_app
