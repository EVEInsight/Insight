from InsightUtilities import InsightSingleton
from InsightSubsystems.Cron import CronManager
import InsightLogger
import asyncio
import InsightExc
import time
import traceback


class AbstractCronTask(metaclass=InsightSingleton):
    def __init__(self, cron_manager):
        self.cron_manager: CronManager.CronManager = cron_manager
        self.insight_ready_event = self.cron_manager.insight_ready_event
        self.lg = InsightLogger.InsightLogger.get_logger('Cron.{}'.format(self.__class__.__name__),
                                                         'Cron.log', child=True)
        self.client = self.cron_manager.client
        self.loop = self.cron_manager.loop
        self.service = self.cron_manager.service
        self.zk = self.cron_manager.zk
        self.channel_manager = self.client.channel_manager
        self.config = self.service.config
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
                await asyncio.sleep(2)
            except Exception as ex:
                self.lg.exception(ex)
                traceback.print_exc()
                print("Error when running cron task. {} - EX: {}".format(self.__class__.__name__, ex))
                await asyncio.sleep(55)
            finally:
                await asyncio.sleep(self.get_wait_time())

    async def start_loop(self):
        self.task = self.cron_manager.loop.create_task(self.cron_loop())
