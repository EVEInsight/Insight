from InsightSubsystems.Cron.CronTasks.AbstractCronTask import AbstractCronTask


class ChannelAutoRefresh(AbstractCronTask):
    def __init__(self, cron_manager):
        super().__init__(cron_manager)

    def call_now(self) -> bool:
        return False

    def loop_iteration(self) -> int:
        return 60

    async def _run_task(self):
        await self.channel_manager.refresh_post_all_tasks()
