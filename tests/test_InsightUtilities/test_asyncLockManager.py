from tests.abstract import AsyncTesting
from InsightUtilities import AsyncLockManager
import asyncio


class TestAsyncLockManager(AsyncTesting.AsyncTesting):
    def setUp(self):
        super().setUp()
        self.lockManager = AsyncLockManager()

    def test_get_object_none(self):
        """passing none should return a brand new lock and not store anything in the dictionary"""
        lock_1 = self.loop.run_until_complete(self.lockManager.get_object(None))
        self.assertIsInstance(lock_1, asyncio.Lock)
        lock_2 = self.loop.run_until_complete(self.lockManager.get_object(None))
        self.assertIsInstance(lock_2, asyncio.Lock)
        self.assertNotEqual(lock_1, lock_2)
        self.assertEqual({}, self.lockManager.pool)

    def test_get_object_id(self):
        lock_1 = self.loop.run_until_complete(self.lockManager.get_object(5))
        self.assertIsInstance(lock_1, asyncio.Lock)
        lock_2 = self.loop.run_until_complete(self.lockManager.get_object(5))
        self.assertEqual(lock_1, lock_2)
        self.assertEqual(1, len(self.lockManager.pool))
        lock_3_new_id = self.loop.run_until_complete(self.lockManager.get_object(6))
        self.assertIsInstance(lock_3_new_id, asyncio.Lock)
        self.assertNotEqual(lock_3_new_id, lock_1)
        self.assertEqual(2, len(self.lockManager.pool))
        self.assertEqual(lock_2, self.loop.run_until_complete(self.lockManager.get_object(5)))
