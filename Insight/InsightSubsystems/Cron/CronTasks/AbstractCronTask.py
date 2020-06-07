from InsightUtilities import InsightSingleton
from InsightSubsystems.Cron import CronManager
import InsightLogger
import asyncio
import InsightExc
import time


class AbstractCronTask(metaclass=InsightSingleton):
    def __init__(self, cron_manager):
        self.cm: CronManager.CronManager = cron_manager
        self.insight_ready_event = self.cm.insight_ready_event
        self.lg = InsightLogger.InsightLogger.get_logger('Cron.{}'.format(self.__class__.__name__),
                                                         'Cron.log', child=True)
        self.client = self.cm.client
        self.loop = self.cm.loop
        self.service = self.cm.service
        self.zk = self.cm.zk
        self.channel_manager = self.client.channel_manager
        self.task: asyncio.Task = None

    def loop_iteration(self) -> int:
        raise NotImplementedError

    def run_at_intervals(self) -> bool:
        return False

    def interval_offset(self) -> int:
        return 0

    def call_now(self) -> bool:
        return False

    def get_wait_time(self) -> int:
        if self.run_at_intervals():
            offset = self.interval_offset()
            interval = self.loop_iteration()
            if offset >= interval:
                raise InsightExc.baseException.InsightException(message="Cron offset cannot be greater than interval")
            else:
                return int((interval - (time.time() % interval)) + offset)
        else:
            return self.loop_iteration()

    async def _run_task(self):
        raise NotImplementedError

    async def cron_loop(self):
        await self.insight_ready_event.wait()
        if not self.call_now():
            await asyncio.sleep(self.get_wait_time())
        while True:
            try:
                st = InsightLogger.InsightLogger.time_start()
                await self._run_task()
                InsightLogger.InsightLogger.time_log(self.lg, st, "Execute cron task {}".
                                                     format(self.__class__.__name__), seconds=False)
            except Exception as ex:
                self.lg.exception(ex)
            finally:
                await asyncio.sleep(self.get_wait_time())

    async def start_loop(self):
        self.task = self.cm.loop.create_task(self.cron_loop())
