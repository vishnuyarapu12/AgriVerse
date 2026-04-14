"""
Delayed reminders using APScheduler (BackgroundScheduler).
On fire: prints and logs "REMINDER: <message>".
"""
import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple

from apscheduler.schedulers.background import BackgroundScheduler

logger = logging.getLogger(__name__)

_scheduler: Optional[BackgroundScheduler] = None


def _fire_reminder(message: str) -> None:
    """Runs in worker thread when the job fires."""
    line = f"REMINDER: {message}"
    print(line, flush=True)
    logger.info("%s", line)


def get_scheduler() -> BackgroundScheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = BackgroundScheduler(timezone=timezone.utc)
    return _scheduler


def start_scheduler() -> None:
    sched = get_scheduler()
    if not sched.running:
        sched.start()
        logger.info("APScheduler started (UTC)")


def shutdown_scheduler() -> None:
    sched = get_scheduler()
    if sched.running:
        sched.shutdown(wait=False)
        logger.info("APScheduler shut down")


def schedule_reminder(message: str, delay_seconds: int) -> Tuple[str, datetime]:
    """
    Schedule a one-shot reminder. Returns (job_id, run_at_utc).
    """
    sched = get_scheduler()
    run_at = datetime.now(timezone.utc) + timedelta(seconds=delay_seconds)
    job_id = f"r_{uuid.uuid4().hex[:16]}"

    sched.add_job(
        _fire_reminder,
        trigger="date",
        run_date=run_at,
        args=[message],
        id=job_id,
        replace_existing=False,
        misfire_grace_time=300,
    )
    logger.info("Scheduled reminder job_id=%s at %s", job_id, run_at.isoformat())
    return job_id, run_at
