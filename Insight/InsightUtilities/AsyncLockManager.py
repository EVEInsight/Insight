import InsightLogger
import asyncio


class AsyncLockManager(object):
    def __init__(self, event_loop=None):
        self.pool = {}
        self.logger = InsightLogger.InsightLogger.get_logger('InsightUtilities.AsyncLockManager',
                                                             'InsightUtilities.log', child=True)
        if event_loop is None:
            self.lock = asyncio.Lock(loop=asyncio.get_event_loop())
        else:
            self.lock = asyncio.Lock(loop=event_loop)

    async def get_object(self, key, limit: int = 1):
        async with self.lock:
            try:
                if key is None:
                    raise ValueError
                value_object = self.pool.get(key)
                if not isinstance(value_object, asyncio.Lock):
                    value_object = asyncio.Lock()
                    self.pool[key] = value_object
                    self.logger.info('Created new: {} for key: {}'.format(type(value_object), key))
                else:
                    self.logger.info('Got existing: {} for key: {}'.format(type(value_object), key))
                return value_object
            except Exception as ex:
                self.logger.exception(ex)
                return asyncio.Lock()
