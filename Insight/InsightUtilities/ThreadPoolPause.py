import InsightExc
from concurrent.futures import ThreadPoolExecutor
import asyncio
import threading
import datetime
import InsightLogger


class ThreadPoolPause(object):
    def __init__(self, thread_pool, timeout: int = 30):
        self.threadpool: ThreadPoolExecutor = thread_pool
        self.timeout = timeout
        self.thread_count = self.threadpool._max_workers
        if self.thread_count == 0:
            raise InsightExc.Internal.ThreadPauseExc("Cannot pause limitless threadpool.")
        self.logger = InsightLogger.InsightLogger.get_logger('InsightUtilities.ThreadPoolPause', 'InsightUtilities.log', child=True)

        self.__lock_count = threading.Lock()
        self.__acquire_count = 0
        self.__play_thread = threading.Event()

    def block_thread(self):
        if not self.__play_thread.is_set():
            with self.__lock_count:
                self.__acquire_count += 1
            self.logger.debug("Thread block acquired.")
            self.__play_thread.wait()
            self.logger.debug("Thread block released.")

    async def __aenter__(self):
        self.logger.info("Entering context for pausing thread pool.")
        try:
            self.__play_thread.clear()
            self.__acquire_count = 0
            self.max_delay = datetime.datetime.utcnow() + datetime.timedelta(seconds=self.timeout)
            for i in range(0, self.thread_count):
                asyncio.get_event_loop().run_in_executor(self.threadpool, self.block_thread)
            while self.__acquire_count != self.thread_count:
                if datetime.datetime.utcnow() >= self.max_delay:
                    raise InsightExc.Internal.ThreadPauseTimeout
                await asyncio.sleep(.1)
        except InsightExc.Internal.ThreadPauseTimeout as ex:
            self.__play_thread.set()
            raise ex

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.logger.info("Exiting context for releasing thread pool.")
        self.__play_thread.set()
