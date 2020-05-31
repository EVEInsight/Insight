from InsightSubsystems.Cron.CronTasks.AbstractCronTask import AbstractCronTask
from InsightSubsystems.Cache.CacheEndpoint import LastShip


class LastShipPreCache(AbstractCronTask):
    def __init__(self, cron_manager):
        super().__init__(cron_manager)
        self.LastShip: LastShip = LastShip()

    def loop_iteration(self) -> int:
        return 60

    async def _run_task(self):
        await self.LastShip.cron_precache_operation()
