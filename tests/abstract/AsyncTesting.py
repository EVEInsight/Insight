import asyncio
from tests.abstract import InsightTestBase
from concurrent.futures import ThreadPoolExecutor
from threading import Thread
from tests.mocks.ConfigLoader import ConfigLoader


class AsyncTesting(InsightTestBase.InsightTestBase):
    def setUp(self):
        super().setUp()
        self.config: ConfigLoader = ConfigLoader()
        self.loop = asyncio.new_event_loop()
        self.thread_Pool = ThreadPoolExecutor(max_workers=1)
        self.loop.set_default_executor(self.thread_Pool)
        asyncio.set_event_loop(self.loop)
        self._loop_thread = Thread(target=self._run_loop)

    def tearDown(self):
        super().tearDown()
        if self.loop.is_running():
            for t in asyncio.Task.all_tasks():
                self.loop.call_soon_threadsafe(t.cancel)
            self.loop.call_soon_threadsafe(self.loop.stop)
        if self._loop_thread.isAlive():
            self._loop_thread.join()
        asyncio.set_event_loop(None)

    def _run_loop(self):
        try:
            self.loop.run_forever()
        finally:
            self.loop.run_until_complete(self.loop.shutdown_asyncgens())
            self.loop.close()

    def start_event_loop(self):
        self._loop_thread.start()
