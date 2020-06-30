from InsightSubsystems.Cron.CronTasks.AbstractCronTask import AbstractCronTask
import InsightLogger
from functools import partial
from database.db_tables import tb_tokens


class SyncContacts(AbstractCronTask):
    def __init__(self, cron_manager):
        super().__init__(cron_manager)
        self.lg_tokens = InsightLogger.InsightLogger.get_logger('Tokens', 'Tokens.log')
        self.suppress_notify = True

    def loop_iteration(self) -> int:
        return self.config.get("CRON_SYNCCONTACTS")

    def run_at_intervals(self) -> bool:
        return False

    def call_now(self) -> bool:
        return False

    async def __helper_update_contacts_channels(self):
        st = InsightLogger.InsightLogger.time_start()
        async for channel in self.channel_manager.get_all_channels():
            try:
                await channel.background_contact_sync(message=None, suppress=self.suppress_notify)
            except Exception as ex:
                print(ex)
                self.lg_tokens.exception(ex)
        self.suppress_notify = False
        InsightLogger.InsightLogger.time_log(self.lg_tokens, st, "Update/reload channels", seconds=True)

    async def _run_task(self):
        try:
            st = InsightLogger.InsightLogger.time_start()
            await self.loop.run_in_executor(None, partial(tb_tokens.mass_sync_all, self.service))
            await self.loop.run_in_executor(None, partial(tb_tokens.delete_noTracking, self.service))
            await self.__helper_update_contacts_channels()
            InsightLogger.InsightLogger.time_log(self.lg_tokens, st, "Total sync contacts task.", seconds=True)
        except Exception as ex:
            print(ex)
            raise ex
