from tests.abstract import AsyncTesting
from InsightUtilities import AsyncSemaphoreManager
import asyncio


class TestAsyncSemaphoreManager(AsyncTesting.AsyncTesting):
    def setUp(self):
        super().setUp()
        self.semManager = AsyncSemaphoreManager()

    def test_get_object_none(self):
        """passing none should return a brand new lock and not store anything in the dictionary"""
        sem_1 = self.loop.run_until_complete(self.semManager.get_object(None))
        self.assertIsInstance(sem_1, asyncio.Semaphore)
        sem_2 = self.loop.run_until_complete(self.semManager.get_object(None))
        self.assertIsInstance(sem_2, asyncio.Semaphore)
        self.assertNotEqual(sem_1, sem_2)
        self.assertEqual({}, self.semManager.pool)

    def test_get_object_id(self):
        sem_1 = self.loop.run_until_complete(self.semManager.get_object(5, 3))
        self.assertIsInstance(sem_1, asyncio.Semaphore)
        self.assertEqual(3, sem_1._value)
        sem_2 = self.loop.run_until_complete(self.semManager.get_object(5, 2))
        self.assertEqual(sem_1, sem_2)
        self.assertEqual(3, sem_2._value) # changing count should return initially created semaphore
        self.assertEqual(1, len(self.semManager.pool))
        sem_3_new_id = self.loop.run_until_complete(self.semManager.get_object(6, 3))
        self.assertIsInstance(sem_3_new_id, asyncio.Semaphore)
        self.assertNotEqual(sem_3_new_id, sem_1)
        self.assertEqual(2, len(self.semManager.pool))
        self.assertEqual(sem_2, self.loop.run_until_complete(self.semManager.get_object(5, 3)))
