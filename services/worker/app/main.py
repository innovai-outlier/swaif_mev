"""Worker startup entrypoint."""
from __future__ import annotations

import logging
import os

from app.celery_app import celery_app
from app.config import settings


def configure_logging() -> None:
    """Configure base logging format for worker runtime."""
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format='%(asctime)s %(levelname)s %(name)s %(message)s',
    )


def run() -> None:
    """Run celery worker, beat, or both depending on runtime mode."""
    configure_logging()
    logger = logging.getLogger(__name__)

    mode = (os.getenv('CELERY_RUN_MODE') or settings.celery_run_mode).lower()
    logger.info('Starting worker runtime with mode=%s broker=%s backend=%s', mode, settings.broker_url, settings.result_backend)

    argv = ['worker', '--loglevel', settings.log_level.lower()]
    if mode == 'beat':
        argv = ['beat', '--loglevel', settings.log_level.lower()]
    elif mode == 'both':
        argv.append('--beat')
    elif mode != 'worker':
        logger.warning('Unknown mode %s, falling back to worker-only', mode)

    celery_app.worker_main(argv)


if __name__ == '__main__':
    run()
