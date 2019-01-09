from .AsyncLockManager import AsyncLockManager
import asyncio


class AsyncSemaphoreManager(AsyncLockManager):

    async def get_object(self, key, limit: int = 1):
        async with self.lock:
            try:
                if key is None:
                    raise ValueError
                value_object = self.pool.get(key)
                if not isinstance(value_object, asyncio.Semaphore):
                    value_object = asyncio.Semaphore(value=limit)
                    self.pool[key] = value_object
                    self.logger.info('Created new: {} for key: {}'.format(type(value_object), key))
                else:
                    self.logger.info('Got existing: {} for key: {}'.format(type(value_object), key))
                return value_object
            except Exception as ex:
                self.logger.exception(ex)
                return asyncio.Semaphore(value=limit)

