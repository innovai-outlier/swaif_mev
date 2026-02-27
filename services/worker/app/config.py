"""Runtime settings for the worker service."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class WorkerSettings(BaseSettings):
    """Environment-backed settings for Celery and DB access."""

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    database_url: str = 'postgresql+psycopg://mevuser:mevpass@localhost:5432/mevdb'
    redis_url: str = 'redis://localhost:6379/0'

    celery_broker_url: str | None = None
    celery_result_backend: str | None = None
    celery_timezone: str = 'UTC'

    streak_recalc_cron: str = '0 2 * * *'
    badge_assign_cron: str = '0 */6 * * *'
    reminder_cron: str = '0 9,18 * * *'

    celery_run_mode: str = 'both'
    log_level: str = 'INFO'

    @property
    def broker_url(self) -> str:
        return self.celery_broker_url or self.redis_url

    @property
    def result_backend(self) -> str:
        return self.celery_result_backend or self.redis_url


settings = WorkerSettings()
