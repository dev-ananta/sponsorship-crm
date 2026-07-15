import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

logger = logging.getLogger(__name__)


class SchedulerService:
    def __init__(self, timezone: str = "UTC") -> None:
        self.scheduler = AsyncIOScheduler(timezone=timezone)

    def start(self) -> None:
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("scheduler_started")

    def shutdown(self) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            logger.info("scheduler_stopped")
