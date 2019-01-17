import asyncio
from tests.abstract import InsightTestBase
from concurrent.futures import ThreadPoolExecutor


class AsyncTesting(InsightTestBase.InsightTestBase):
    def setUp(self):
        super().setUp()
        self.loop = asyncio.new_event_loop()
        self.loop.set_default_executor(ThreadPoolExecutor(max_workers=1))
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        super().tearDown()
        asyncio.set_event_loop(None)
