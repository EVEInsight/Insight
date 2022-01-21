from InsightSubsystems.Cron.CronTasks.AbstractCronTask import AbstractCronTask
from database.db_tables.eve.mass_name_resolve import name_resolve

class ResolveNonEntityNames(AbstractCronTask):
    def __init__(self, cron_manager):
        super().__init__(cron_manager)
        self.error_ids_404 = {}
        self.error_ids_non404 = {}

    def call_now(self) -> bool:
        return False

    def run_at_intervals(self) -> bool:
        return False

    def loop_iteration(self) -> int:
        return 3600

    def _resolve_names(self):
        name_resolve.api_mass_name_resolve(self.service, error_ids_404=self.error_ids_404,
                                           error_ids_non404=self.error_ids_non404, exclude_nonentity=False,
                                           exclude_entity=True)

    async def _run_task(self):
        await self.loop.run_in_executor(None, self._resolve_names)
