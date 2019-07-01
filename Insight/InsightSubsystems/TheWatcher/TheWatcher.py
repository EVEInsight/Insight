from InsightUtilities import InsightSingleton
import InsightLogger
from service import service
import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import partial


class TheWatcher(metaclass=InsightSingleton):
    def __init__(self, service_module):
        self.service: service.service_module = service_module
        self.systems_id = {}
        self.systems_name = {}
        self.constellations = {}
        self.regions = {}
        self.pilots_id = {}
        self.pilots_name = {}
        self.loop = asyncio.get_event_loop()
        self.kmQueue = asyncio.Queue(maxsize=50000, loop=self.loop)
        self.thread_pool: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=3)
        self.logger = InsightLogger.InsightLogger.get_logger("Watcher.main", "Watcher_main.log", console_print=True)
        InsightLogger.InsightLogger.get_logger("Watcher.systems", "Watcher_systems.log")
        InsightLogger.InsightLogger.get_logger("Watcher.pilots", "Watcher_pilots.log")

    async def submit_km_noblock(self, km):
        self.loop.create_task(self.kmQueue.put(km))

    async def submit_km(self, km):
        await self.kmQueue.put(km)

    async def start_coroutines(self):
        self.loop.create_task(self.coroutine_dequeue())
        self.loop.create_task(self.coroutine_enqueue())

    async def load_historical_data(self):
        self.logger.info("Started historical data load.")

    async def coroutine_enqueue(self):
        self.logger.info('The Watcher (pilot ship and system tracker) enqueue coroutine started.')

    async def coroutine_dequeue(self):
        self.logger.info('The Watcher (pilot ship and system tracker) dequeue coroutine started.')
        #loop.create_task(self.load_all_kms())
        while True:
            try:
                km = await self.kmQueue.get()
                km = None  # does not do anything yet
                #await loop.run_in_executor(self.thread_pool, partial(self.process_km, km))
            except Exception as ex:
                print(ex)
