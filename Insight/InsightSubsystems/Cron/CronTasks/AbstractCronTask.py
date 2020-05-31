from InsightUtilities import InsightSingleton
from InsightSubsystems.Cron import CronManager
import InsightLogger
import asyncio


class AbstractCronTask(metaclass=InsightSingleton):
    def __init__(self, cron_manager):
        self.cm: CronManager.CronManager = cron_manager
        self.insight_ready_event = self.cm.insight_ready_event
        self.lg = InsightLogger.InsightLogger.get_logger('Cron.{}'.format(self.__class__.__name__),
                                                         'Cron.log', child=True)
        self.task: asyncio.Task = None

    def loop_iteration(self) -> int:
        raise NotImplementedError

    def call_now(self) -> bool:
        return False

    async def _run_task(self):
        raise NotImplementedError

    async def cron_loop(self):
        await self.insight_ready_event.wait()
        if not self.call_now():
            await asyncio.sleep(self.loop_iteration())
        while True:
            try:
                await self._run_task()
            except Exception as ex:
                self.lg.exception(ex)
            finally:
                await asyncio.sleep(self.loop_iteration())

    async def start_loop(self):
        self.task = self.cm.loop.create_task(self.cron_loop())
