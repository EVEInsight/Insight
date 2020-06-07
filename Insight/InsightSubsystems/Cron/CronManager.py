from InsightSubsystems.SubsystemBase import SubsystemBase
from InsightSubsystems.Cron import CronTasks


class CronManager(SubsystemBase):
    def __init__(self, subsystemloader):
        super().__init__(subsystemloader)
        self.cron_tasks = {}

    async def start_subsystem(self):
        await self.new_cron_task("LastShipPreCache", CronTasks.LastShipPreCache(cron_manager=self))
        await self.new_cron_task("UpdateDiscordStatus", CronTasks.UpdateDiscordStatus(cron_manager=self))

    async def new_cron_task(self, t_name, cron_task_instance: CronTasks.AbstractCronTask):
        await cron_task_instance.start_loop()
        self.cron_tasks[t_name] = cron_task_instance
