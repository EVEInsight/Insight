from InsightUtilities import InsightSingleton
import InsightLogger
from service import service
import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import partial
import janus
from database.db_tables import tb_kills
from InsightSubsystems.TheWatcher.WatcherTimers import WatcherTimers
import traceback


class TheWatcher(metaclass=InsightSingleton):
    def __init__(self, service_module):
        self.service: service.service_module = service_module
        self.systems_id = {}
        self.systems_name = {}
        self.constellations = {}
        self.regions = {}
        self.pilots_id = {}
        self.pilots_name = {}
        self.processed_mails = set()
        self.loop = asyncio.get_event_loop()
        self.kmQueue = janus.Queue(maxsize=50000, loop=self.loop)
        self.thread_pool: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=1)
        self.logger = InsightLogger.InsightLogger.get_logger("Watcher.main", "Watcher_main.log", console_print=True)
        InsightLogger.InsightLogger.get_logger("Watcher.systems", "Watcher_systems.log")
        InsightLogger.InsightLogger.get_logger("Watcher.pilots", "Watcher_pilots.log")
        self.lock_write = asyncio.Lock(loop=self.loop)
        self.timers = WatcherTimers.WatcherTimers(self)

    async def executor(self, functionPointer, *args):
        return await self.loop.run_in_executor(self.thread_pool, partial(functionPointer, *args))

    async def reset_all(self):
        async with self.lock_write:
            self.logger.info("Clearing all cached data and emptying the mail queue.")
            while True:
                try:
                    await self.kmQueue.async_q.get_nowait()
                except asyncio.QueueEmpty:
                    break
            self.systems_id = {}
            self.systems_name = {}
            self.constellations = {}
            self.regions = {}
            self.pilots_id = {}
            self.pilots_name = {}
            self.processed_mails = set()
            self.logger.info("Finished clearing all cached data and mail queue.")

    async def submit_km_noblock(self, km):
        self.loop.create_task(self.kmQueue.async_q.put(km))

    async def submit_km(self, km):
        await self.kmQueue.async_q.put(km)

    def submit_km_sync_block(self, km):
        self.kmQueue.sync_q.put(km)

    async def run_setup_tasks(self):
        self.loop.create_task(self.coroutine_dequeue())
        #self.loop.create_task(self.coroutine_enqueue())
        await self.timers.start_tasks()

    async def coroutine_dequeue(self):
        self.logger.info('The Watcher (pilot ship and system tracker) dequeue coroutine started.')
        while True:
            try:
                km: tb_kills = await self.kmQueue.async_q.get()
                async with self.lock_write:
                    km_id = km.kill_id
                    if km_id not in self.processed_mails:
                        #await loop.run_in_executor(self.thread_pool, partial(self.process_km, km))
                        self.processed_mails.add(km_id)
            except Exception as ex:
                self.logger.exception("Enqueue mail")
