import asyncio
from tests.abstract import InsightTestBase


class AsyncTesting(InsightTestBase.InsightTestBase):
    def setUp(self):
        super().setUp()
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        super().tearDown()
        asyncio.set_event_loop(None)
