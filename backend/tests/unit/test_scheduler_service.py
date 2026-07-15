import pytest

from app.services.scheduler import SchedulerService


@pytest.mark.asyncio
async def test_scheduler_start_and_shutdown() -> None:
    service = SchedulerService()
    service.start()
    assert service.scheduler.running is True
    service.shutdown()
    assert service.scheduler.running is False
