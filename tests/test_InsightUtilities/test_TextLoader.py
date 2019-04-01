from tests.abstract import AsyncTesting
from InsightUtilities import InsightSingleton, TextLoader
import asyncio


class TestTextLoader(AsyncTesting.AsyncTesting):
    def setUp(self):
        super().setUp()
        self.start_event_loop()

    def tearDown(self):
        super().tearDown()
        InsightSingleton.clear_instance_references()

    def test_getReference(self):
        """double check we dont create two separate instance"""
        self.assertEqual(TextLoader(), TextLoader())

    def test_getValidText(self):
        self.assertEqual("This is a greeting demo text file.", TextLoader.text_sync("demo.greeting", "en"))
        self.assertEqual("This is a greeting demo text file.", TextLoader()._textCache.get("demo.greeting_en"))

    def test_getInvalidText(self):
        self.assertEqual("The text path was not found: demo.greeting_ru", TextLoader.text_sync("demo.greeting", "ru"))
        self.assertEqual("The text path was not found: demo.greeting_ru", TextLoader()._textCache.get("demo.greeting_ru"))

    def test_asyncGetValid(self):
        result = asyncio.run_coroutine_threadsafe(TextLoader.text_async("demo.greeting", "en"), self.loop).result()
        self.assertEqual("This is a greeting demo text file.", result)
        self.assertEqual("This is a greeting demo text file.", TextLoader()._textCache.get("demo.greeting_en"))