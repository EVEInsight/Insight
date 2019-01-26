from tests.abstract import AsyncTesting
from InsightUtilities import ThreadPoolPause
from concurrent.futures import ThreadPoolExecutor
import threading
import asyncio
import time
import InsightExc


class TestThreadPoolPause(AsyncTesting.AsyncTesting):
    def setUp(self):
        super().setUp()
        self.start_event_loop()
        self.threadPool = ThreadPoolExecutor(max_workers=5)
        self.threadPause = ThreadPoolPause(self.threadPool, timeout=1)
        self.counter = 0
        self.lock = threading.Lock()

    def test_block_thread(self):
        for i in range(0, 10):
            self.loop.run_in_executor(self.threadPool, self.threadPause.block_thread)
        self.assertEqual(5, self.threadPause._acquire_count)
        self.threadPause._play_thread.set()
        for i in range(0, 10):
            self.loop.run_in_executor(self.threadPool, self.thread_increment_counter)
        time.sleep(.1)
        self.assertEqual(10, self.counter)

    def thread_increment_counter(self):
        with self.lock:
            self.counter += 1

    def thread_blocking(self):
        while self.loop.is_running():
            time.sleep(.5)

    async def async_test_aenter_timeout(self):
        for i in range(0, 10):
            self.loop.run_in_executor(self.threadPool, self.thread_blocking)
        with self.assertRaises(InsightExc.Internal.ThreadPauseTimeout):
            async with self.threadPause:
                pass

    async def async_test_aenter(self):
        async with self.threadPause:
            for i in range(0, 10):
                self.loop.run_in_executor(self.threadPool, self.thread_increment_counter)
            await asyncio.sleep(.1)
            self.assertEqual(0, self.counter)
            for t in self.threadPool._threads:
                self.assertTrue(t.is_alive())
            self.assertEqual(5, self.threadPause._acquire_count)
        await asyncio.sleep(.1)
        self.assertEqual(10, self.counter)
        for i in range(0, 10):
            self.loop.run_in_executor(self.threadPool, self.thread_increment_counter)
        await asyncio.sleep(.1)
        self.assertEqual(20, self.counter)

    def test_aenter(self):
        f = asyncio.run_coroutine_threadsafe(self.async_test_aenter(), self.loop)
        f.result()

    def test_aenter_timeout(self):
        f = asyncio.run_coroutine_threadsafe(self.async_test_aenter_timeout(), self.loop)
        f.result()
