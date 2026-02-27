"""Worker entrypoint with Celery tasks for protocol recomputation."""
import os
from celery import Celery


REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

celery_app = Celery("mev_worker", broker=REDIS_URL, backend=REDIS_URL)


@celery_app.task(name="recompute_protocol_run")
def recompute_protocol_run(protocol_run_id: int):
    """Placeholder task for protocol run recomputation."""
    return {
        "protocol_run_id": protocol_run_id,
        "status": "queued",
        "message": "Recompute placeholder executed",
    }


if __name__ == "__main__":
    celery_app.worker_main(["worker", "--loglevel=info"])
