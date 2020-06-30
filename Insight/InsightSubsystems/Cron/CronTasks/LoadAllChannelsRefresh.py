from InsightSubsystems.Cron.CronTasks.AbstractCronTask import AbstractCronTask


class LoadAllChannelsRefresh(AbstractCronTask):
    def __init__(self, cron_manager):
        super().__init__(cron_manager)

    def call_now(self) -> bool:
        return False

    def loop_iteration(self) -> int:
        return 1800

    async def _run_task(self):
        await self.channel_manager.load_channels(load_message=False)
