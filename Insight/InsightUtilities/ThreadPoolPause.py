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

        self._lock_count = threading.Lock()
        self._acquire_count = 0
        self._play_thread = threading.Event()

    def block_thread(self):
        if not self._play_thread.is_set():
            with self._lock_count:
                self._acquire_count += 1
            self.logger.debug("Thread block acquired.")
            self._play_thread.wait()
            self.logger.debug("Thread block released.")

    async def __aenter__(self):
        self.logger.info("Entering context for pausing thread pool.")
        try:
            self._play_thread.clear()
            self._acquire_count = 0
            self.max_delay = datetime.datetime.utcnow() + datetime.timedelta(seconds=self.timeout)
            for i in range(0, self.thread_count):
                asyncio.get_event_loop().run_in_executor(self.threadpool, self.block_thread)
            while self._acquire_count != self.thread_count:
                if datetime.datetime.utcnow() >= self.max_delay:
                    raise InsightExc.Internal.ThreadPauseTimeout
                await asyncio.sleep(.1)
        except InsightExc.Internal.ThreadPauseTimeout as ex:
            self._play_thread.set()
            raise ex

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.logger.info("Exiting context for releasing thread pool.")
        self._play_thread.set()
