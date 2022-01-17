from InsightSubsystems.Cron.CronTasks.AbstractCronTask import AbstractCronTask
from InsightSubsystems.Cache.CacheEndpoint import LastShip


class LastShipPreCache(AbstractCronTask):
    def __init__(self, cron_manager):
        super().__init__(cron_manager)
        self.LastShip: LastShip = LastShip()
        self._loop_iteration_override = max(60, self.service.config.get("SUBSYSTEM_CACHE_LASTSHIP_PRECACHE_SECONDS"))
        if self.service.config.get("SUBSYSTEM_CACHE_LASTSHIP_PRECACHE_SECONDS") > 0:
            print("LastShip precache is enabled and is scheduled to run every {} seconds.".format(self._loop_iteration_override))

    def loop_iteration(self) -> int:
        return self._loop_iteration_override

    async def _run_task(self):
        await self.LastShip.cron_precache_operation()
